__author__ = 'Lothilius'

# The primary purpose of this script is to return data from a csv or api source and package it as
# a tde file so that it can be used within Tableau.
# The script converts the data in to a panda Dataframe in order to analyze and maintain data structure.

import pandas as pd
import sys
from datetime import date
from tableausdk import *
from tableausdk.Extract import *



# Define type maps
schemaIniTypeMap = {
    'bool' :     Type.BOOLEAN,
    'bytes':     Type.INTEGER,
    'int64':  Type.INTEGER,
    'float64':   Type.DOUBLE,
    'Date':     Type.DATE,
    'datetime64[ns]': Type.DATETIME,
    'object':     Type.UNICODE_STRING,
}

class TDEAssembler (object):
    def __init__(self, dataframe='', file_path='', extract_name=''):
        """ Initialize new assembler
        :return: None
        """
        self.dataframe = dataframe
        self.file_path = file_path
        self.extract_name = extract_name

        # Check the type of data passed to the assembler
        try:
            if type(self.dataframe) is pd.DataFrame:
                self.assemble_tde()
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    def assemble_tde(self):
        """ Gather the data information and create the Tde.
        :return:
        """
        data_meta = pd.DataFrame(test.dtypes.reset_index())
        data_meta.rename(columns={'index': 'column_name', 0: 'data_type'}, inplace=True)

        # Create the Table referance
        deptdata = Extract("DeptData.tde")   #assign your output name

        # table_definition = TableDefinition()

        print data_meta
        print data_meta.as_matrix()[3][1]

        if self.file_path == '':
            print "no file path"

if __name__ == '__main__':
    now = date.today()
    print type(now)
    test = pd.DataFrame(columns=['col1', 'col2', 'col3', 'col4'], data=[[1, 2.3, u'a', now]])
    TDEAssembler(test)