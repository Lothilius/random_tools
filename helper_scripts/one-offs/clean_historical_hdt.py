__author__ = 'Lothilius'

import re
import csv
import pandas as pd
from HTMLParser import HTMLParser


class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def read_in_csv():
    try:
        # Read a csv file
        with open('temp/place_holder.csv', 'rb') as f:
            reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_list = list(reader)
        return csv_list
    except csv.Error:
        field_limit = csv.field_size_limit()
        csv.field_size_limit(field_limit + 1000)
        read_in_csv()


def main(your_list, master_list, clean_list, new_list, b_history):
    # Read File as block of Text
    with open('some_file.csv', 'rb') as f:
        file_as_list = f.readlines()

    # string_from_file.split('\r')

    html_clean_list = []
    for each in file_as_list:
        html_clean_list.append(strip_tags(each))

    regex = re.compile(r'[\n\r\t=*-+]')
    white_space_clean = []
    for each in html_clean_list:
        value = strip_tags(each)
        clean_value = regex.sub(' ', value)
        clean_value = ' '.join(clean_value.split())
        white_space_clean.append(clean_value)


    # Write each line as a line if no \n at end of line
    with open('temp/place_holder.csv', 'w+') as the_file:
        for s in white_space_clean:
            the_file.write(s + '\n')


    csv_list = read_in_csv()

    true_master = []
    for k, each in enumerate(csv_list):
        row_list = []
        for j, item in enumerate(each):
            if len(each) == len(csv_list[0]):
                row_list.append(item)
            elif len(row_list[-1]) < len(csv_list[0]):
                if len(row_list[-1]) + len(csv_list[k+1]) < len(csv_list[0]):
                    row_list[-1][-1] = row_list[-1][-1] + item
                elif len(each) + len(csv_list[k+1]) == len(csv_list[0]):
                    row_list.append(item)
                elif len(csv_list[k+1]) == len(csv_list[0]) or len(row_list[-1]) + len(each) == len(csv_list[0]):
                    row_list.append(item)

        true_master.append(row_list)




# Reduce whitespace
true_master = []
regex = re.compile(r'[\n\r\t,\\\']')
for k, each in enumerate(csv_clean_list):
    row_list = []
    for j, item in enumerate(each):
        clean_value = regex.sub(' ', item)
        clean_value = ' '.join(clean_value.split())
        row_list.append(clean_value)

    true_master.append(row_list)

# Check if the line starts with an ID
for each in your_list:
    try:
        int(each[0])
        master_list.append(each)
    except:
        pass


# Reduce whitespace
ready_master = []
regex = re.compile(r'[\n\r\t,\\\']')
for k, each in enumerate(csv_clean_list):
    row_list = []
    for j, item in enumerate(each):
        clean_value = regex.sub(' ', item)
        clean_value = ' '.join(clean_value.split())
        row_list.append(clean_value)

    true_master.append(row_list)

clean_master = []
for k, each in enumerate(true_master):
    row_list = []
    for j, item in enumerate(each):
        if len(row_list) < 624:
            row_list.append(clean_value)
        else:
            break

    clean_master.append(row_list)


clean_master = []
row_list = []
for k, each in enumerate(true_master):
  for j, item in enumerate(each):
      if len(row_list) < 624:
          row_list.append(item)
      elif len(row_list) == 624:
          row_list.append(item)
          clean_master.append(row_list)
          row_list = []
      else:
          break

# Drop columns with all NA values
b_history.dropna(axis=1, how='all', inplace=True)

# Convert Id column to ints or Nan if errror on conversion
b_history['Id'] = b_history['Id'].apply(lambda x: pd.to_numeric(x, errors=coerce))

# Drop rows with Id value as Nan
b_history = b_history[pd.notnull(b_history['Id'])]

# Get first 40 Columns
b_history.ix[:,:40]

b_history['Id'] = b_history['Id'].astype(int)