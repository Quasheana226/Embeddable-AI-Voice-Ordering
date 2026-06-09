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
    # TODO: Remove punctuation, special characters, and normalize whitespace
    return None


def get_keywords(text):
    # TODO: Extract meaningful keywords by filtering out NLTK stopwords
    return None


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
    """
    Send a .wav audio file to IBM Watson Speech-to-Text and return the transcript.

    Args:
        file_name (str): Full path to the .wav audio file.

    Returns:
        str: The transcribed text from the audio.
    """
    # IBM Watson STT API endpoint
    speech_to_text_url = "https://sn-watson-stt.labs.skills.network/speech-to-text/api/v1/recognize"

    # Tell the API we're sending a .wav file
    headers = {"Content-Type": "audio/wav"}

    # Model config:
    # - en-US_Multimedia: optimized for English audio from mic/media sources
    # - smart_formatting: auto-formats dates, numbers, currency in the transcript
    # - background_audio_suppression: 0.6 filters out background noise (range 0-1)
    params = {
        "model": "en-US_Multimedia",
        "smart_formatting": "true",
        "background_audio_suppression": "0.6"
    }

    # POST the audio file as binary data to the Watson STT service
    result = requests.post(
        speech_to_text_url,
        headers=headers,
        params=params,
        data=open(file_name, 'rb')
    )

    # Parse the JSON response and concatenate all transcript alternatives
    output = ""
    json_obj = json.loads(result.text)
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
    # mode="bx" ensures we don't accidentally overwrite an existing file
    with open(name, mode="bx") as f:
        f.write(request.content)