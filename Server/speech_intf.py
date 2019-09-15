import os, requests, time
from xml.etree import ElementTree
import azure.cognitiveservices.speech as speechsdk

speech_key, service_region = "50314f04a9ec4b0aa3241691c5d67d12", "westus"
subscription_key = "50314f04a9ec4b0aa3241691c5d67d12"

fname = "myfile.wav"

class SpeechProcessor(object):
    def __init__(self):
        self.subscription_key = subscription_key
        self.access_token = None

    def get_token(self):
        fetch_token_url = "https://westus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def tts_process(self, text): #text-to-speech, takes text, returns fname
        base_url = 'https://westus.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set('name', 'en-US-Guy24kRUS') # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
        voice.text = str(text)
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)

        if response.status_code == 200:
            with open('resp' + '.wav', 'wb') as audio:
                audio.write(response.content)
                return "resp.wav"
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")

    def stt_process(self, audio_file): #speech-to-text, takes fname, returns recognized text
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        self.audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)

        result = self.speech_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            #print(str(result.text))
            return str(result.text)

        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(result.no_match_details))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
