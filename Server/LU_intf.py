import requests

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': 'abb8d490d73345b7a11d0e8b6319b7bd',
}

def get_intent(transcript):
    params ={
        # Query parameter
        'q': transcript,
        # Optional request parameters, set to default values
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }

    try:
        r = requests.get('https://lutest.cognitiveservices.azure.com/luis/v2.0/apps/a73cdc58-4ea1-44af-bc83-18c57374d29d',headers=headers, params=params)
        resp = r.json()['topScoringIntent']['intent']
        print("LU response: " + str(resp))
        return resp
    except:
        transcript = transcript.split()
        if ('looking' in transcript) and ('at' in transcript):
            print("describing scene")
            return "QualitativeScene"
        elif ('in' in transcript) and ('front' in transcript):
            print("finding object in front")
            return "InFront"
        elif 'that' in transcript:
            print("what's that")
            return "WhatsThat"
        else:
            return None