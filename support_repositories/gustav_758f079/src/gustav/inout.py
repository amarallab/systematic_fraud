import os

from pathlib import Path

import pandas as pd


def get_data_version(dataset):
        
    default_settings = 'reference_data_plosbio_2022'

    settings = _settings_from_file()
    
    
    code_dir = settings['code']
    
    
    def _load_from_json(use_path):
        import json
        p = os.path.join(code_dir, f'{use_path}.json')
        with open(p) as d:
            reference_data_versions = json.load(d)
        return reference_data_versions
    
    def _load_from_yaml(use_path):
        import yaml
        p = os.path.join(code_dir, f'{use_path}.yml')
        reference_data_versions = yaml.safe_load(Path(p).read_text())
        return reference_data_versions
    
    
    
    if os.path.exists(os.path.join(code_dir, 'reference_data_custom.yml')):
        if os.path.exists(os.path.join(code_dir, 'reference_data_custom.json')):
            raise AssertionError(
                """reference_data_custom.yml and reference_data_custom.json file
                are simulateneously present. Please remove one of them.""")
        else:
            reference_data_versions = _load_from_yaml('reference_data_custom')          
    elif os.path.exists(os.path.join(code_dir, 'reference_data_custom.json')):
        reference_data_versions=_load_from_json('reference_data_custom')
    elif os.path.exists(os.path.join(code_dir, f'{default_settings}.json')):
        reference_data_versions=_load_from_json(default_settings)                                 
    else:
        raise AssertionError('Could not find settings for gustav data environment.')
        
    
    data_version = reference_data_versions[dataset]
    return data_version


def get_input_path(extension=None, flavor='default'):
    '''
    Returns subfolder within input folder of gustav.

    Input:
        extension   str, optional, subfolder
    Output:
        outpath     str, folder within internal part of gustav
    '''

    if extension is not None:
        extension = _adjust_to_current_file_separator(extension)
    
    settings = _settings_from_file()
    
    
    if flavor == 'default':
        base_folder = settings['input_main']
    elif flavor == 'big':
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
        'gustav.csv'
    )

    if not os.path.exists(path_to_settings):
        raise EnvironmentError(rf"""
            Could not find gustav.csv file:
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
            gustav.csv must start with the two
            columns: key and value.
            
            {path_to_settings}
        """)
        
        
    settings = settings.drop_duplicates()
    
    if any(settings['key'].duplicated()):
        raise EnvironmentError(rf"""
            At least one key within gustav.csv is
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