__author__ = 'Lothilius'

# The primary purpose of this script is to return data from a csv or api source and package it as
# a tde file so that it can be used within Tableau.
# The script converts the data in to a panda Dataframe in order to analyze and maintain data structure.

import pandas as pd
from os import environ
from datetime import datetime
from tableausdk import *
from tableausdk.Extract import *
import numpy as np


# Define type maps
schema_type_map = {
    'bool' :     Type.BOOLEAN,
    'bytes':     Type.INTEGER,
    'int64':  Type.INTEGER,
    'float64':   Type.DOUBLE,
    'datetime64[ns]': Type.DATETIME,
    'object':     Type.UNICODE_STRING
}


class TDEAssembler (object):
    def __init__(self, data_frame, file_path='', extract_name=''):
        """ Initialize new assembler
        :return: None
        """
        self.data_frame = data_frame
        if file_path == '' and os.environ['MY_ENVIRONMENT'] == 'prod':
            self.file_path = '/var/shared_folder/BizApps/Tableau_data/'
        elif file_path == '':
            self.file_path = '/Users/%s/Downloads/' % environ['USER']
        else:
            self.file_path = file_path

        self.time_of_extract = datetime.now()
        self.extract_name = extract_name

        # Check the type of data passed to the assembler
        try:
            if isinstance(self.data_frame, pd.DataFrame):
                self.assemble_tde()
        except ValueError:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    def __str__(self):
        return self.tde_file()

    def assemble_tde(self):
        """ Gather the data information and create the Tde.
        :return:
        """
        #  Create time stamp and Apply the time of extract to the data frame and the name of the file
        self.add_timestamp(self.time_of_extract)
        file_name = self.tde_file()
        data_meta = pd.DataFrame(self.data_frame.dtypes.reset_index())
        data_meta.rename(columns={'index': 'column_name', 0: 'data_type'}, inplace=True)

        print "Creating extract:", file_name

        ExtractAPI.initialize()

        with Extract(file_name) as data_extract:
            table = None
            table_definition = None

            if not data_extract.hasTable('Extract'):
                table_definition = TableDefinition()
                for each in data_meta.as_matrix():
                    # Add the column info to the table definition
                    if 'date' in str(each[0]).lower():
                        table_definition.addColumn(str(each[0]), schema_type_map['datetime64[ns]'])
                    else:
                        table_definition.addColumn(str(each[0]), schema_type_map[str(each[1])])
                # Create the Table with the table definition
                table = data_extract.addTable("Extract", table_definition)


            new_row = Row(table_definition)
            for i in range(self.data_frame.shape[0]):
                for j, item in enumerate(data_meta['column_name'].tolist()):
                    self.add_to_row(new_row, j, self.data_frame[item].iloc[i], data_meta['data_type'][j])
                table.insert(new_row)

            data_extract.close()

    def add_timestamp(self, time_of_extract):
        """ Create a column stamping all the tickets with the date and time of the extract.
        :return: None. Appends to the data frame a column with the time and date of the extract.
        """
        self.data_frame['Extract_Timestamp'] = time_of_extract


    @staticmethod
    def add_to_row(row_object, column_number, value, value_type):
        """ Convert the value and add it to the row object given.
        :param row_object: The row object of the table
        :param column_number: The column number for the value you are adding
        :param value: The value you are adding. Must be of panda dtype bytes, int64, float64, or datetime64[ns]
        :param value_type: The type for the column given.
        :return:
        """
        value_type = str(value_type)
        try:
            if column_number != 35:
                value = datetime.combine(value, datetime.min.time())
                value_type = 'datetime64[ns]'
        except:
            try:
                if column_number != 35:
                    value = datetime.strptime(value, '%Y-%m-%d')
                    value_type = 'datetime64[ns]'
            except:
                pass
        if value == None or str(value) == str(np.nan):
            value = 'NA'
        if value == False or value == True:
            value = str(value)
        if value_type == 'bool':
            row_object.setBoolean(column_number, value)
        elif value_type == 'bytes':
            row_object.setInteger(column_number, value)
        elif value_type == 'int64':
            if value == 'NA':
                value = 0
            row_object.setLongInteger(column_number, value)
        elif value_type == 'float64':
            if isinstance(value, str):
                value = float(0.0)
            row_object.setDouble(column_number, value)
        elif value_type == 'datetime64[ns]':
            # Split the datetime in to its components
            if value == 'NA':
                value = datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            year = value.year
            month = value.month
            day = value.day
            hour = value.hour
            min = value.minute
            sec = value.second
            try:
                frac = value.microsecond / 10000
            except:
                frac = 0
            row_object.setDateTime(column_number, year, month, day,	hour, min, sec, frac)
        else:
            row_object.setString(column_number, value)

if __name__ == '__main__':
    now = datetime.now()
    today = datetime.today()
    test = pd.DataFrame(columns=['col1', 'col2', 'col3', 'col4'], data=[[1, 2.3, 'a', now],
                                                                        [2, 3.3, 'b', today]])
    TDEAssembler(data_frame=test)
