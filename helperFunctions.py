import os
import glob
import json
import requests
import pandas as pd
from zipfile import ZipFile
from difflib import SequenceMatcher
from nltk.corpus import stopwords
import nltk

# Download NLTK stopwords if not already present (needed for NLP text processing)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

def clean_text(text):
    """
    Remove common English stopwords and pizza-ordering filler words from the transcript.
    Returns empty string if text is None (e.g. recording failed or was empty).
    """
    if not text:
        return ""

    stop_words = stopwords.words("english")
    stop_words.extend([
        "gimme", "lemme", "cause", "cuz", "imma", "gonna", "wanna", "please", "the", "and",
        "gotta", "hafta", "woulda", "coulda", "shoulda", "howdy", "day", "can", "could",
        "my", "mine", "I" "hey", "yoo", "deliver", "delivery", "delivered", "piece", "want",
        "send", "sent", "order", "pizza", "piz", "pizze", "address", "addrez", "to", "too"
    ])
    clean_texts = " ".join([
        word.replace("X", "").replace("/", "")
        for word in text.split()
        if word.lower() not in stop_words
    ])
    return clean_texts


def get_keywords(text):
    if not text:
        return [], []



def play_local_wav_file(file_name):
    """Stream a local .wav file in 1024-byte chunks for audio playback."""
    with open(str("./" + file_name), "rb") as wav:
        data = wav.read(1024)
        while data:
            # Yield each chunk so it can be streamed without loading the full file into memory
            yield data
            data = wav.read(1024)


def read_zip_file(zip_name):
    """Extract a .zip archive and return a sorted list of .wav file paths inside it."""
    files = str(os.getcwd() + "/" + zip_name + ".zip")
    # Extract all contents of the zip into the current working directory
    with ZipFile(files, "r") as zip_object:
        zip_object.extractall()
    # Build a glob pattern to find all .wav files in the extracted folder
    path = str(os.getcwd() + "/" + zip_name + "/*.wav")
    folder = glob.glob(path)
    # Return files sorted in ascending order for consistent processing
    return sorted(folder, reverse=False)


def save_audio(file, file_name):
    """Save an uploaded audio file object to disk at the given file path."""
    with open(file_name, "wb") as audio:
        file.save(audio)
    print("file uploaded successfully")

def speech_to_text(file_name):
    speech_to_text_url = "https://sn-watson-stt.labs.skills.network/speech-to-text/api/v1/recognize"
    headers = {"Content-Type": "audio/wav"}
    params = {
        "model": "en-US_Multimedia",
        "smart_formatting": "true",
        "background_audio_suppression": "0.6"
    }
    result = requests.post(
        speech_to_text_url,
        headers=headers,
        params=params,
        data=open(file_name, 'rb')
    )

    output = ""
    json_obj = json.loads(result.text)

    # Guard: if no results key or empty results, return empty string
    if "results" not in json_obj or not json_obj["results"]:
        print("STT returned no results — audio may have been too short or silent")
        return output

    results_data = json_obj["results"]
    for r in results_data:
        for transcript in r["alternatives"]:
            output = output + " " + transcript["transcript"]

    return output


def text_to_speech(texts, name, language):
    """
    Convert a text string to a .wav audio file using IBM Watson Text-to-Speech.

    Args:
        texts (str): The text to be converted to speech.
        name (str): Output filename for the generated .wav file (e.g. 'output.wav').
        language (str): Watson voice model to use (e.g. 'en-US_MichaelV3Voice').
    """
    # Delete any existing file with the same name to avoid write conflicts
    bash_command = str("find . -path \*/" + name + " -delete")
    os.system(bash_command)

    # IBM Watson TTS API endpoint
    text_to_speech_url = "https://sn-watson-tts.labs.skills.network/text-to-speech/api/v1/synthesize?output=output_text.wav"

    # Send JSON text input, expect a .wav audio file back
    headers = {"Content-Type": "application/json", "Accept": "audio/wav"}

    # Voice tuning parameters:
    # - rate_percentage: speech speed (-2 = slightly slower than default)
    # - pitch_percentagequery: voice pitch (0 = default pitch)
    # - voice: selects the Watson voice/language model
    params = {
        "rate_percentage": -2,
        "pitch_percentagequery": 0,
        "voice": language
    }

    # Wrap the input text in JSON format as required by the Watson TTS API
    words = json.dumps({"text": texts})

    # POST the text to Watson TTS and receive the synthesized audio
    request = requests.post(text_to_speech_url, headers=headers, params=params, data=words)

    # Log the HTTP status — 200 means success, anything else indicates an error
    print(request.status_code)
    if request.status_code != 200:
        print("TTS Service status:", request.text)
        print("Creating file ---", name)

    # Write the raw audio bytes to disk as a .wav file
    # mode="wb" ensures we don't accidentally overwrite an existing file
    with open(name, mode="wb") as f:
        f.write(request.content)