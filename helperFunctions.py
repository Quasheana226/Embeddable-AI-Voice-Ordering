import os
import glob
import json
import requests
import pandas as pd
from zipfile import ZipFile
from difflib import SequenceMatcher
from nltk.corpus import stopwords
import nltk

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


def clean_text(text):
    # TODO
    return None


def get_keywords(text):
    # TODO
    return None


def play_local_wav_file(file_name):
    with open(str("./" + file_name), "rb") as wav:
        data = wav.read(1024)
        while data:
            yield data
            data = wav.read(1024)


def read_zip_file(zip_name):
    files = str(os.getcwd() + "/" + zip_name + ".zip")
    with ZipFile(files, "r") as zip_object:
        zip_object.extractall()
    path = str(os.getcwd() + "/" + zip_name + "/*.wav")
    folder = glob.glob(path)
    return sorted(folder, reverse=False)


def save_audio(file, file_name):
    with open(file_name, "wb") as audio:
        file.save(audio)
    print("file uploaded successfully")


def speech_to_text(file_name):
    speech_to_text_url = "https://sn-watson-stt.labs.skills.network/speech-to-text/api/v1/recognize"
    headers = {"Content-Type": "audio/wav"}
    params = {"model": "en-US_Multimedia", "smart_formatting": "true", "background_audio_suppression": "0.6"}
    result = requests.post(speech_to_text_url, headers=headers, params=params, data=open(file_name, 'rb'))
    output = ""
    json_obj = json.loads(result.text)
    results_data = json_obj["results"]
    for r in results_data:
        for transcript in r["alternatives"]:
            output = output + " " + transcript["transcript"]
    return output


def text_to_speech(texts, name, language):
    # TODO
    return None