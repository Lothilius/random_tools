# -*- coding: utf-8 -*-
__author__ = 'Lothilius'

# The primary purpose of this script is to return data from a csv or api source and package it as
# a hyper file so that it can be used within Tableau.
# The script converts the data in to a panda Dataframe in order to analyze and maintain data structure.

import pandas as pd
from os import environ
from datetime import datetime
from tableausdk2 import *
from tableausdk2.HyperExtract import *
import numpy as np
from pyprogressbar import Bar
from os.path import expanduser
import pandas as pd
from os import remove
import boto3


# Define type maps
schema_type_map = {
    'bool' :     Type.BOOLEAN,
    'bytes':     Type.INTEGER,
    'int64':  Type.INTEGER,
    'float64':   Type.DOUBLE,
    'datetime64[ns]': Type.DATETIME,
    'object':     Type.UNICODE_STRING
}


class HyperAssembler (object):
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
        self.last_data_row_extracted = None
        self.error = None

        # Check the type of data passed to the assembler
        try:
            if isinstance(self.data_frame, pd.DataFrame):
                # Create time stamp and Apply the time of extract to the data frame and the name of the file
                self.add_timestamp(self.time_of_extract)
                self.file_name = self.extract_file()

                self.data_types = self.assess_type()
                self.assemble_extract()
        except Exception as e:
            the_errors = e
            error_result = "Unexpected error 1: %s, %s, %s" % (sys.exc_info()[0], sys.exc_info()[1], str(the_errors))
            raise Exception(error_result)

    def __str__(self):
        return self.file_name

    def assess_type(self):
        data_meta = pd.DataFrame(self.data_frame.dtypes)
        data_meta.rename(columns={0: 'data_type'}, inplace=True)

        return data_meta

    def assemble_extract(self):
        """ Gather the data information and create the Tde.
        :return:
        """
        try:
            print "Creating extract:", self.file_name

            ExtractAPI.initialize()

            with Extract(self.file_name) as data_extract:
                # If extract Does exist add to the Extract table and file
                if data_extract.hasTable('Extract'):
                    # Open an existing table to add more rows
                    table = data_extract.openTable('Extract')
                    table_definition = table.getTableDefinition()
                else:
                    table_definition = TableDefinition()
                    for each in self.data_types.reset_index(level=0).values:
                        # Add the column info to the table definition
                        table_definition.addColumn(str(each[0]), schema_type_map[str(each[1])])
                    # Create the Table with the table definition
                    table = data_extract.addTable("Extract", table_definition)

                new_row = Row(table_definition)
                count = self.data_frame.shape[0]
                pbar = Bar(count)

                # Run through dataframe data and add data to the table object
                for i in range(count):
                    for j, column_name in enumerate(self.data_types.index.values.tolist()):
                        self.add_to_row(new_row, j, self.data_frame[column_name].iloc[i],
                                        self.data_types['data_type'][j], column_name)
                    table.insert(new_row)

                    self.last_data_row_extracted = self.data_frame.iloc[i].to_frame().transpose()
                    # if i == 1:
                    #     raise Exception
                    pbar.passed()

            data_extract.close()
            ExtractAPI.cleanup()

            if self.error is not None:
                raise Exception
        except:
            file_name = self.extract_file()

            # Clean up resources
            Extract(file_name).close()
            ExtractAPI.cleanup()

            # Create pickle of the data
            full_filename = self.file_name.replace('.hyper', '_pickle')
            print full_filename
            # offending_dataf
            self.data_frame.to_pickle(path=full_filename)

            # Load File to S3
            # Create an S3 client
            s3 = boto3.client('s3')
            bucket_name = 'biztech-tableau-data-files'
            s3_file_path = 'BizApps/Tableau_data/%s' % self.extract_name
            # Uploads the given file using a managed uploader, which will split up large
            # files automatically and upload parts in parallel.
            s3.upload_file(full_filename, bucket_name, s3_file_path)
            remove(full_filename)

            raise Exception("Error in creating hyper file please consult data files. \n%s. \n%s, \n%s, \n%s. \n%s"
                            % (full_filename, sys.exc_info()[0], sys.exc_info()[1],
                               'Error on line {}'.format(sys.exc_info()[-1].tb_lineno), self.error))

    def add_timestamp(self, time_of_extract):
        """ Create a column stamping all the tickets with the date and time of the extract.
        :return: None. Appends to the data frame a column with the time and date of the extract.
        """
        self.data_frame['Extract_Timestamp'] = time_of_extract

    def extract_file(self):
        """ Use this in conjuction with the data publisher in order to publish the data.
        :return: File name and path to the hyper extract file
        """
        # Create filename with path, name a time stamp
        now = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        if self.extract_name == '':
            self.extract_name = 'tableau_extract_file'
        file_name = '%s%s_%s.hyper' % (self.file_path, self.extract_name, now)

        return file_name

    def add_to_row(self, row_object, column_number, value, value_type, column_name):
        """ Convert the value and add it to the row object given.
        :param row_object: The row object of the table
        :param column_number: The column number for the value you are adding
        :param value: The value you are adding. Must be of panda dtype bytes, int64, float64, or datetime64[ns]
        :param value_type: The type for the column given.
        :return: Nothing
        """

        column_type = self.data_types.loc[column_name][0]

        if str(value_type) == column_type:
            value_type = str(value_type)
        else:
            value_type = column_type

        try:
            if value == None or str(value) == str(np.nan):
                value = 'NA'
            if value == False or value == True:
                value = str(value)
            if value_type == 'bool':
                if value == "True":
                    value = True
                else:
                    value = False
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
                if isinstance(value, str):
                    row_object.setCharString(column_number, value.encode(encoding='ascii', errors='ignore'))
                else:
                    row_object.setCharString(column_number, str(value).encode(encoding='ascii', errors='ignore'))
        except:
            if self.error is None:
                self.error = ''
            value = value.encode(encoding="ascii", errors='ignore')
            # Create pickle of the offending dataframe.
            self.error += "Value: %s, Value Type: %s, column name%s: %s, %s \n" \
                          % (value, value_type, column_number, column_name, type(value))


if __name__ == '__main__':
    ticket_list = pd.read_pickle('/Users/martin.valenzuela/Downloads/BizApps_HDT__pickle')
    # data_file = TDEAssembler(data_frame=ticket_list, extract_name='EUS_testing_fixxxxed')


