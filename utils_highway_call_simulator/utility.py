""" Utility """

import argparse
import datetime
import json
import logging
import os

class DictClass:
    """ Creating class from dictionary """
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DictClass(value))
            else:
                setattr(self, key, value)

def init_logger(log_dir, file_name, level):
    """ Initialise logger """
    ensure_dir(log_dir)
    log_file = os.path.join(log_dir, file_name+'_'+get_now_str()+'.log')
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        level=level,
        format='%(asctime)s [%(levelname)s][%(message)s]'
    )

def get_now_str():
    """ get current time in %Y-%m-%d_%H-%M format """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M")

def ensure_dir(file_dir):
    """ Ensure the directory exist """
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

def load_settings(file_path="settings.json", detail=""):
    """ load settings """
    settings = {}
    with open(file_path, 'r') as input_file:
        settings = json.load(input_file)
    if detail != "":
        return DictClass(settings[detail])
    return DictClass(settings)

def get_settings_path_from_arg(description):
    """ Parse command line arguments for setting file """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--settings',
        dest='settings',
        type=str,
        default='settings.json',
        help='path of the settings file')

    return parser.parse_args().settings
