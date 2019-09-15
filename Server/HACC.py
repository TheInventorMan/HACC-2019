from os.path import isfile, join
import os

def list_files(mypath=os.path.dirname(__file__)):
    return [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
    # list files in same dir

def rm_jpg():
    for file in list_files():
        if file.endswith('.jpg') or file.endswith('.jpeg'):
            os.remove(file)

from adb.client import Client as AdbClient
client = AdbClient(host="localhost", port=5037)
device = client.device("emulator-5554")

device.pull("/Phone/AudioRecorder/audio.wav", "audio.wav")
#print(list_files('C:\\Users\\georg\\Desktop'))
