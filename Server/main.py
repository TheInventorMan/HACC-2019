from image_intf import ImageProcessor
from speech_intf import SpeechProcessor
from LU_intf import get_intent
from Depth.depth_intf import DepthMap

import numpy as np
import cv2
import sys
from matplotlib import pyplot as plt
import pyaudio
import wave
import winsound

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 3
cmd = "command.wav"
#start server

#init
dmap = DepthMap()
imgproc = ImageProcessor()
speechproc = SpeechProcessor()
speechproc.get_token()

img = "image.jpg"

debug = False
fallback = True

def main(aud_file, img_file):
    transcript = speechproc.stt_process(aud_file).lower()[:-1]
    print("Detected transcript: " + transcript)
    intent = get_intent(transcript)

    if intent == "QualitativeScene":
        resp = describe_scene(img_file, quant=False)
        print("describing scene")
    elif intent == "QuantitativeScene":
        resp = describe_scene(img_file, quant=True)
        print("describing scene (quant)")
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
        cropped = depth_map[:,:,obj[3]:obj[4], obj[1]:obj[2]]
        #print(depth_map.shape)
        #print(obj[3], obj[4], obj[1], obj[2])
        #print(cropped.shape)
        avg_disp = np.mean(cropped)
        #print(avg_disp)
        dist = 22.5*0.54*721/(1242*avg_disp)
        #print(dist)
        dist = str(int(max(dist, 0.01)))

        if dist != "1":
            s = "s"
        else:
            s = ""

        if (obj[1]+obj[2])/2 < l_thresh:
            left.append(obj[0] + ", about " + dist + " meter" + s + " away")
        elif (obj[1]+obj[2])/2 > r_thresh:
            right.append(obj[0] + ", about " + dist + " meter" + s + " away")
        else:
            if (obj[3]+obj[4])/2 < h_thresh:
                distance.append(obj[0] + ", about " + dist + " meter" + s + " away")
            else:
                front.append(obj[0] + ", about " + dist + " meter" + s + " away")

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

def closest_to_center(img_file):
    r_val = imgproc.get_img_objects(img_file)
    objects = r_val[0]

    c_x = r_val[1][0]/2
    c_y = r_val[1][1]/2

    centered = ""
    lowest_euc_dist = 1000000

    for obj in objects:
        img_x = (obj[1]+obj[2])/2
        img_y = (obj[3]+obj[4])/2
        dist = np.sqrt((img_x-c_x)**2 + (img_y-c_y)**2)
        if dist < lowest_euc_dist:
            lowest_euc_dist = dist
            centered = obj[0]
    return centered


#fcn: get 3d map. send image to imageproc and get labels and bboxes
#send image to depth map and make 3d space

def describe_scene(img_file, quant):
    captions = imgproc.get_img_captions(img_file)
    top_caption = "I see " + str(captions[0])

    phrase = top_caption + ". "

    if quant:
        positions = get_3d_map(img_file)
    else:
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
        front = front + positions[0] + positions[1] #expand window to entire frame

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
    closest = closest_to_center(img_file)
    if closest == "":
        return "There doesn't seem to be anything there. "
    else:
        phrase = "I see a " + closest + " over there. "

    return phrase

def parse_resp(resp):
    fname = speechproc.tts_process(resp)
    print("Speaking:" + resp)
    return fname

while True and debug:
    command = input("enter command:")
    cmd_aud = speechproc.tts_process(command)

    resp = main('resp.wav', img) #send audio and img files to main method

    print(parse_resp(resp)) #final file to send back to android

while True and fallback:
    _ = input("Hit any key to begin recording (3 sec)")
    #halt exec, press key to record audio
    print("Capturing image...")
    video_capture = cv2.VideoCapture(1)
    # Check success
    if not video_capture.isOpened():
        raise Exception("Could not open video device")
        # Read picture. ret === True on success
    ret, frame = video_capture.read()
    # Close device
    video_capture.release()
    cv2.imwrite("test.jpg", frame)
    print("Done!")

    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    print("Recording...")

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(cmd, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    resp = main("command.wav", "test.jpg")
    fname = parse_resp(resp)
    #play file fname
    winsound.PlaySound(fname, winsound.SND_FILENAME)

def exec(a_fname, i_fname):
    resp = main(a_fname, i_fname)
    print(parse_resp(resp))
