__author__ = 'Lothilius'

# The primary purpose of this script is to return data from a csv or api source and package it as
# a tde file so that it can be used within Tableau.
# The script converts the data in to a panda Dataframe in order to analyze and maintain data structure.

import pandas as pd
import sys


class TDEAssembler (object):
    def __init__(self, dataframe='', file_path=''):
        """ Initialize new assembler
        :return: None
        """
        self.dataframe = dataframe
        self.file_path = file_path

        # Check the type of data passed to the assembler
        try:
            if type(self.dataframe) is pd.DataFrame:
                return self.assemble_tde()
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    def assemble_tde(self):
        """ Gather the data information and create the Tde
        :return:
        """
        data_meta = pd.DataFrame(test.dtypes.reset_index())
        data_meta.rename(columns={'index': 'column_name', 0: 'data_type'}, inplace=True)

        if self.file_path == '':
            print "no file path"

        print data_meta[['column_name', 'data_type']]

if __name__ == '__main__':
    test = pd.DataFrame(columns=['col1', 'col2', 'col3'], data=[[1, 2.3, 'a']])
    TDEAssembler(test)