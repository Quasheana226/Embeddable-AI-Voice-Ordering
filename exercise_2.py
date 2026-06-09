from helperFunctions import text_to_speech

# All available Watson TTS voice models (English, French, Italian)
languages = [
    "en-GB_CharlotteV3Voice", "en-GB_JamesV3Voice", "en-GB_KateV3Voice",
    "en-US_AllisonV3Voice", "en-US_EmilyV3Voice", "en-US_HenryV3Voice",
    "en-US_KevinV3Voice",
    "en-US_LisaV3Voice", "en-US_MichaelV3Voice", "en-US_OliviaV3Voice",
    "fr-CA_LouiseV3Voice", "fr-FR_NicolasV3Voice", "fr-FR_ReneeV3Voice",
    "it-IT_FrancescaV3Voice"
]

# Text to synthesize
texts = "Hello world, I am from IBM Watson Text-to-Speech Library."

# Output filename for the generated audio
name = "test_1.wav"


def tts_testing(text, file_name, language):
    """Call text_to_speech and save the result to file_name using the given voice."""
    text_to_speech(text, file_name, language)


# Run the test using the Kevin (en-US) voice — change languages[6] to try others
tts_testing(texts, name, languages[6])