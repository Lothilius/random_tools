__author__ = 'Lothilius'


from os import path


def get_static_file(file_name=''):
    file_path = path.dirname(__file__)
    full_path = file_path + '/' + file_name
    if path.isfile(full_path):
        return full_path
    else:
        # TODO - Improve error handeling here.
        raise IOError


if __name__ == '__main__':
    print get_static_file('styleTags.html')