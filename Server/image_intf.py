from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import os
import sys
import time

subscription_key = "64f0eeff90354ce4b6d803c53010863d"
endpoint = "https://hacccv.cognitiveservices.azure.com/"
local_image_path = "C:\\test.jpg"

class ImageProcessor(object):
    def __init__(self):
        self.computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    
    def get_img_captions(self, image_path):
        local_image = open(image_path, "rb")
        local_image_description = self.computervision_client.describe_image_in_stream(local_image)
        captions = []
        if (len(local_image_description.captions) == 0):
            print("No captions detected.")
        else:
            for caption in local_image_description.captions:
                captions.append(caption.text)

        return captions
    
    def get_img_objects(self, image_path):
        local_image = open(image_path, "rb")
        local_image_objects = self.computervision_client.detect_objects_in_stream(local_image)
        objects = []
        if len(local_image_objects.objects) == 0:
            print("No objects detected.")
        else:
            for obj in local_image_objects.objects:
                objects.append((obj.object_property, obj.rectangle.x, obj.rectangle.x + obj.rectangle.w, \
                                obj.rectangle.y, obj.rectangle.y + obj.rectangle.h))
                                
        dims = (local_image_objects.metadata.width, local_image_objects.metadata.height)

        return (objects, dims)