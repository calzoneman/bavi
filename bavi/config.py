import configparser

def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config
