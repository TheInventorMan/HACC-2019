from image_intf import ImageProcessor
from speech_intf import SpeechProcessor
from LU_intf import get_intent
from Depth.depth_intf import DepthMap

import numpy as np

#start server

#init
dmap = DepthMap()
imgproc = ImageProcessor()
speechproc = SpeechProcessor()
speechproc.get_token()

img = "image.jpg"

def main(aud_file, img_file):
    transcript = speechproc.stt_process(aud_file).lower()[:-1]
    print(transcript)
    intent = get_intent(transcript)

    if intent == "QualitativeScene":
        resp = describe_scene(img_file)
        print("describing scene")
    elif intent == "InFront":
        resp = in_front(img_file)
        print("finding object in front")
    elif intent == "WhatsThat":
        resp = whats_that(img_file)
        print("what's that")
    else:
        resp = "Sorry, I don't understand. "

    return resp


def get_3d_map(img_file):
    depth_map = dmap.get_depth_map(img_file)
    r_val = imgproc.get_img_objects(img_file)
    objects = r_val[0]

    width = r_val[1][0]
    height = r_val[1][1]

    l_thresh = width/3
    r_thresh = 2*width/3
    h_thresh = height/2

    left = []
    right = []
    front = []
    distance = []

    for obj in objects:
        cropped = depth_map[obj[3]:obj[4], obj[1]:obj[2]]
        avg_disp = np.mean(cropped)
        dist = 22.5*0.54*721/(1242*avg_disp)
        if (obj[1]+obj[2])/2 < l_thresh:
            left.append(obj[0] + ", about " + str(int(dist)) + " meters away")
        elif (obj[1]+obj[2])/2 > r_thresh:
            right.append(obj[0] + ", about " + str(int(dist)) + " meters away")
        else:
            if (obj[3]+obj[4])/2 < h_thresh:
                distance.append(obj[0] + ", about " + str(int(dist)) + " meters away")
            else:
                front.append(obj[0] + ", about " + str(int(dist)) + " meters away")

    return (left, right, front, distance)


def get_2d_map(img_file):
    r_val = imgproc.get_img_objects(img_file)
    objects = r_val[0]

    width = r_val[1][0]
    height = r_val[1][1]

    l_thresh = width/3
    r_thresh = 2*width/3
    h_thresh = height/2

    left = []
    right = []
    front = []
    distance = []

    for obj in objects:
        if (obj[1]+obj[2])/2 < l_thresh:
            left.append(obj[0])
        elif (obj[1]+obj[2])/2 > r_thresh:
            right.append(obj[0])
        else:
            if (obj[3]+obj[4])/2 < h_thresh:
                distance.append(obj[0])
            else:
                front.append(obj[0])

    return (left, right, front, distance) #returns only names of objects

#fcn: get 3d map. send image to imageproc and get labels and bboxes
#send image to depth map and make 3d space

def describe_scene(img_file):
    captions = imgproc.get_img_captions(img_file)
    top_caption = "I see " + str(captions[0])

    phrase = top_caption + ". "

    positions = get_2d_map(img_file)

    for idx in range(len(positions)):
        if len(positions[idx]) == 0:
            continue
        if idx == 0:
            if len(positions[idx]) == 1:
                phrase = phrase + "On the left, I see a " + positions[idx][0] + ". "
            elif len(positions[idx]) == 2:
                phrase = phrase + "On the left, I see a " + positions[idx][0] + " and a " + positions[idx][1] + ". "
            else:
                phrase = phrase + "On the left, I see "
                for i in range(len(positions[idx])-1):
                    phrase = phrase + "a " + positions[idx][i] + ", "
                phrase = phrase + "and a " + positions[idx][-1] + ". "

        elif idx == 1:
            if len(positions[idx]) == 1:
                phrase = phrase + "On the right, I see a " + positions[idx][0] + ". "
            elif len(positions[idx]) == 2:
                phrase = phrase + "On the right, I see a " + positions[idx][0] + " and a " + positions[idx][1] + ". "
            else:
                phrase = phrase + "On the right, I see "
                for i in range(len(positions[idx])-1):
                    phrase = phrase + "a " + positions[idx][i] + ", "
                phrase = phrase + "and a " + positions[idx][-1] + ". "

        elif idx == 2:
            if len(positions[idx]) == 1:
                phrase = phrase + "Just ahead, I see a " + positions[idx][0] + ". "
            elif len(positions[idx]) == 2:
                phrase = phrase + "Just ahead, I see a " + positions[idx][0] + " and a " + positions[idx][1] + ". "
            else:
                phrase = phrase + "Just ahead, I see "
                for i in range(len(positions[idx])-1):
                    phrase = phrase + "a " + positions[idx][i] + ", "
                phrase = phrase + "and a " + positions[idx][-1] + ". "

        elif idx == 3:
            if len(positions[idx]) == 1:
                phrase = phrase + "In the distance, I see a " + positions[idx][0] + ". "
            elif len(positions[idx]) == 2:
                phrase = phrase + "In the distance, I see a " + positions[idx][0] + " and a " + positions[idx][1] + ". "
            else:
                phrase = phrase + "In the distance, I see "
                for i in range(len(positions[idx])-1):
                    phrase = phrase + "a " + positions[idx][i] + ", "
                phrase = phrase + "and a " + positions[idx][-1] + ". "

    return phrase

def in_front(img_file):
    positions = get_2d_map(img_file)
    front = positions[2] + positions[3]
    phrase = ""
    if len(front) == 0:
        return "There doesn't seem to be anything there. "

    if len(front) == 1:
        phrase = phrase + "In the front, I see a " + front[0] + ". "
    elif len(front) == 2:
        phrase = phrase + "In the front, I see a " + front[0] + " and a " + front[1] + ". "
    else:
        phrase = phrase + "In the front, I see "
        for i in range(len(front)-1):
            phrase = phrase + "a " + front[i] + ", "
        phrase = phrase + "and a " + front[-1] + ". "
    return phrase

def whats_that(img_file):
    positions = get_2d_map(img_file)
    front = positions[2] + positions[3]
    phrase = ""
    if len(front) == 0:
        return "There doesn't seem to be anything there. "

    if len(front) == 1:
        phrase = phrase + "I see a " + front[0] + ". "
    elif len(front) == 2:
        phrase = phrase + "I see a " + front[0] + " and a " + front[1] + ". "
    else:
        phrase = phrase + "I see "
        for i in range(len(front)-1):
            phrase = phrase + "a " + front[i] + ", "
        phrase = phrase + "and a " + front[-1] + ". "
    return phrase

def parse_resp(resp):
    fname = speechproc.tts_process(resp)
    print("Speaking:" + resp)
    return fname

while True:
    command = input("enter command:")
    cmd_aud = speechproc.tts_process(command)

    resp = main('resp.wav', img)

    print(parse_resp(resp))