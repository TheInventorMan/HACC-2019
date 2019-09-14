# <snippet_imports>
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import os
import sys
import time
# </snippet_imports>

subscription_key = "64f0eeff90354ce4b6d803c53010863d"

endpoint = "https://hacccv.cognitiveservices.azure.com/"

# <snippet_client>
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
# </snippet_client>

#   Get a local image for analysis
local_image_path = "C:\\test.jpg"
print("\n\nLocal image path:\n" + os.getcwd() + local_image_path)

# Describe a local image by:
#   1. Opening the binary file for reading.
#   2. Defining what to extract from the image by initializing an array of VisualFeatureTypes.
#   3. Calling the Computer Vision service's analyze_image_in_stream with the:
#      - image
#      - features to extract
#   4. Displaying the image captions and their confidence values.
local_image = open(local_image_path, "rb")
local_image_description = computervision_client.describe_image_in_stream(local_image)

print("\nCaptions from local image: ")
if (len(local_image_description.captions) == 0):
    print("No captions detected.")
else:
    for caption in local_image_description.captions:
        print("'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100))
#  END - Describe a local image

#   Detect objects in a local image by:
#   1. Opening the binary file for reading.
#   2. Calling the Computer Vision service's detect_objects_in_stream with the:
#      - image
#   3. Displaying the location of the objects.
local_image = open(local_image_path, "rb")
local_image_objects = computervision_client.detect_objects_in_stream(local_image)

print("\nDetecting objects in local image:")
if len(local_image_objects.objects) == 0:
    print("No objects detected.")
else:
    for obj in local_image_objects.objects:
        print((obj.object_property, obj.rectangle.x, obj.rectangle.x + obj.rectangle.w, \
                obj.rectangle.y, obj.rectangle.y + obj.rectangle.h))
                
        print("object at location {}, {}, {}, {}".format( \
        obj.rectangle.x, obj.rectangle.x + obj.rectangle.w, \
        obj.rectangle.y, obj.rectangle.y + obj.rectangle.h))
#   END - Detect objects in a local image


