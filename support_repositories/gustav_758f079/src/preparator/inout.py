import os
from pathlib import Path

import numpy as np
import pandas as pd
from preparator import settings


def get_data_version(dataset):
    data_version = settings.reference_data_versions[dataset]
    return data_version


def ensure_presence_of_directory(directory_path=None):
    '''
    Ensure that the directory of exists. Creates dictionary with cognate
    name in case that directory does not exist. Anticipates that files have
    extensions separated by '.' symbol (can not create directory with . in
    its name); If file does not have an extension separated by '.' a folder
    will with its filname will be created, a behavior that can be avoided
    by calling os.path.dirname prior this function.

    Input:
        directory_path      str; Name of a directory or the full path of a file
    '''
    if directory_path is None:
        raise ValueError('No input specfied for ensure_presence_of_directory')

    directory_path_n, ext = os.path.split(directory_path)

    if '.' in ext:
        directory_path = directory_path_n

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


# def get_intermediate_path(extension=None, big=False):
#     '''
#     Returns subfolder within intermediate folder of gustav.

#     Input:
#         extension   str, optional, subfolder
#         big         default: False
#     Output:
#         outpath     str, folder within intermediate part of gustav
#     '''

#     if big == False:
#         folder = _get_folder('intermediate')
#     elif big == True:
#         folder = _get_folder('big_intermediate')
#     else:
#         raise ValueError('big must either be False or True')

#     if extension is not None:
#         extension = str.replace(extension, '\\', os.path.sep)
#         extension = str.replace(extension, '/', os.path.sep)

#         outpath = os.path.join(folder, extension)
#     else:
#         outpath = folder

#     return outpath


# def get_input_path(extension=None, big=False):
#     '''
#     Returns subfolder within input folder of gustav.

#     Input:
#         extension   str, optional, subfolder
#         big         default: False

#     Output:
#         outpath     str, folder within internal part of gustav
#     '''

#     if big == False:
#         folder = _get_folder('input')
#     elif big == True:
#         folder = _get_folder('big_input')
#     else:
#         raise ValueError('big must either be False or True')

#     if extension is not None:
#         extension = str.replace(extension, '\\', os.path.sep)
#         extension = str.replace(extension, '/', os.path.sep)

#         outpath = os.path.join(folder, extension)
#     else:
#         outpath = folder

#     return outpath


def get_input_path(extension=None, big=False):
    '''
    Returns subfolder within input folder of prepare_gustav.

    Input:
        extension   str, optional, subfolder
    Output:
        outpath     str, folder within input part of prepare_gustav
    '''

    if extension is not None:
        extension = _adjust_to_current_file_separator(extension)

    settings = _settings_from_file()

    if big == False:
        base_folder = settings['input_main']
    elif big == True:
        base_folder = settings['input_big']

    if not os.path.exists(base_folder):
        raise AssertionError(
            'Could not find input folder {}. Please ensure that specified.'.format(
                base_folder))

    if extension is not None:
        extension = str.replace(extension, '\\', os.path.sep)
        extension = str.replace(extension, '/', os.path.sep)

        outpath = os.path.join(base_folder, extension)
    else:
        outpath = base_folder

    return outpath


def get_intermediate_path(extension=None, big=False):
    '''
    Returns subfolder within input folder of prepare_gustav.

    Input:
        extension   str, optional, subfolder
    Output:
        outpath     str, folder within internal part of prepare_gustav
    '''

    if extension is not None:
        extension = _adjust_to_current_file_separator(extension)

    settings = _settings_from_file()

    if big == False:
        base_folder = settings['intermediate_main']
    elif big == True:
        base_folder = settings['intermediate_big']

    if not os.path.exists(base_folder):
        raise AssertionError(
            'Could not find input folder {}. Please ensure that specified.'.format(
                base_folder))

    if extension is not None:
        extension = str.replace(extension, '\\', os.path.sep)
        extension = str.replace(extension, '/', os.path.sep)

        outpath = os.path.join(base_folder, extension)
    else:
        outpath = base_folder

    return outpath


def get_output_path(extension=None, big=False):
    '''
    Returns subfolder within output folder of prepare_gustav.

    Input:
        extension   str, optional, subfolder
    Output:
        outpath     str, folder within output part of prepare_gustav
    '''

    if extension is not None:
        extension = _adjust_to_current_file_separator(extension)

    settings = _settings_from_file()

    if big == False:
        base_folder = settings['output_main']
    elif big == True:
        base_folder = settings['output_big']

    if not os.path.exists(base_folder):
        raise AssertionError(
            'Could not find input folder {}. Please ensure that specified.'.format(
                base_folder))

    if extension is not None:
        extension = str.replace(extension, '\\', os.path.sep)
        extension = str.replace(extension, '/', os.path.sep)

        outpath = os.path.join(base_folder, extension)
    else:
        outpath = base_folder

    return outpath


# def get_output_path(extension=None, big=False):
#     '''
#     Returns subfolder within output folder of gustav.

#     Input:
#         extension   str, optional, subfolder
#     Output:
#         outpath     str, folder within internal part of gustav
#     '''

#     if big == False:
#         folder = _get_folder('output')
#     elif big == True:
#         folder = _get_folder('big_output')
#     else:
#         raise ValueError('big must either be False or True')

#     if extension is not None:
#         extension = str.replace(extension, '\\', os.path.sep)
#         extension = str.replace(extension, '/', os.path.sep)

#         outpath = os.path.join(folder, extension)
#     else:
#         outpath = folder

#     return outpath


def ensure_absence_of_file(file_path):
    """
    Throws error, if path already exists.

    Input:
        file_path   str, path to file or folder
    """

    abs_path = os.path.abspath(file_path)
    if os.path.exists(abs_path):
        raise EnvironmentError('{} already exists'.format(abs_path))


def check_number_of_files_in_directory(dir_path, pattern):
    """
    Counts the number of files in a given directory.extension

    Input:
        dir_path    str, path to folder
        pattern     str, pattern that should be used for finding files

    Output:
        number_of_files     int, number of files in dir_path that match pattern

    """

    from fnmatch import filter

    number_of_files = len(filter(os.listdir(dir_path), pattern))
    return number_of_files


def export_plain_table(df, subpath, big=False, intermediate=False, params=dict()):
    """
    Exports dataframe as plain table with an empty index

    Input:
    df         table to export
    subpath    subpath with gustav output
    big        default False, if True move to alternate storage
                    for big data
    intermediate default False, if True export to intermediate folder
    params     optional; dictionary with parameters for export (note:
                currently supported: only row_group_offsets for
                parquet)
    """

    if intermediate == False:
        p = get_output_path(subpath, big=big)
    elif intermediate == True:
        p = get_intermediate_path(subpath, big=big)
    else:
        raise AssertionError(
            'intermediate must either be False or True')

    ensure_presence_of_directory(p)

    # empty index in a way that is future-proof
    # toward future pandas' export functions
    df.index = np.arange(0, df.shape[0])

    if p.endswith('.parquet'):
        df.to_parquet(p, compression='snappy')

        if 'row_group_size' in params.keys():
            df.to_parquet(
                p,
                compression='snappy',
                row_group_size=params['row_group_size'])

    else:
        raise ValueError(
            'Have not yet implemented chosen file format.')


def _settings_from_file():
    """
    Loads settings from settings file.
    
    Output:
    settings       dict
    
    
    """

    home = str(Path.home())

    path_to_settings = os.path.join(
        str(Path.home()), 'Documents', 'data_paths')

    if not os.path.exists(path_to_settings):
        raise EnvironmentError(rf"""
            Could not find directory reserved for settings:
            {path_to_settings}
        """)

    path_to_settings = os.path.join(
        path_to_settings,
        'prepare_gustav.csv'
    )

    if not os.path.exists(path_to_settings):
        raise EnvironmentError(rf"""
            Could not find prepare_gustav.csv file:
            {path_to_settings}

            This file needs to be UTF-8 formatted
            csv file with two columns: key, value

            Also see readme of repository for
            further guidance.
        """)

    settings = pd.read_csv(
        path_to_settings
    )

    if not all(settings.columns[:2] == ['key', 'value']):
        raise EnvironmentError(rf"""
            prepare_gustav.csv must start with the two
            columns: key and value.
            
            {path_to_settings}
        """)

    settings = settings.drop_duplicates()

    if any(settings['key'].duplicated()):
        raise EnvironmentError(rf"""
            At least one key within prepare_gustav.csv is
            duplicated and therefore ambiguous
            
            {path_to_settings}
        """)

    settings = settings.set_index(
        'key',
        verify_integrity=True
    )['value'].to_dict()

    return settings


def _adjust_to_current_file_separator(x):
    '''
    Replaces backslashes and forward slashes
    by file separtor used on current operating
    system.
    '''
    x = x.replace('\\', os.path.sep)
    x = x.replace('/', os.path.sep)

    return x
