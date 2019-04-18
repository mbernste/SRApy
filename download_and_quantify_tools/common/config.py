import os

def aspera_key_loc():
    if 'ASPERA_KEY' not in os.environ:
        raise Exception("Must set the environment variable 'ASPERA_KEY' to the location of the private key used for aspera")
    return os.environ['ASPERA_KEY']
