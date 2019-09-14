from image_intf import ImageProcessor
from speech_intf import SpeechProcessor

#start server

#init
imgproc = ImageProcessor()
speechproc = SpeechProcessor()
speechproc.get_token()

img = "image.jpg"
while True:
    command = input("enter command:")
    cmd_aud = speechproc.tts_process(command)

    resp = main('resp.wav', img)

    print(parse_resp(resp))


def main(aud_file, img_file):
    transcript = speechproc.stt_process(aud_file).lower().split()
    if 'looking' in transcript and 'at' in transcript:
        resp = describe_scene(img_file)
    elif 'in' in transcript and 'front' in transcript:
        resp = in_front(img_file)
    elif 'that' in transcript:
        resp = whats_that(img_file)
    return resp
#fcn: get audio and image file
# send audio to speechproc to get transcript
#look for keywords
#decision module calls different fcns

def get_3d_map():
    pass
#fcn: get 3d map. send image to imageproc and get labels and bboxes
#send image to depth map and make 3d space

def describe_scene(img_file):
    captions = get_img_captions()
#fcn: describe scene. get 3d map, read caption and all labels by position.

def in_front(img_file):
    pass
#fcn: whats in front. get 3d map, Filter out things not in front, read label

def whats_that(img_file):
    pass
#fcn: what's that. default to whats in front if hand not found. use 3d space and hand
#to figure out pointed object

def parse_resp(resp):
    fname = speechproc.tts_process(resp)
    return fname