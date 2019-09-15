from os.path import isfile, join
import os

def list_files(mypath=os.path.dirname(__file__)):
    return [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
    # list files in same dir

def rm_jpg():
    for file in list_files():
        if file.endswith('.jpg') or file.endswith('.jpeg'):
            os.remove(file)

print(list_files('C:\\Users\\georg\\Desktop'))