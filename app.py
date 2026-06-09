from helperFunctions import *
from flask import Flask, render_template, request, flash, redirect, Response, url_for

app = Flask(__name__)
language, raw_address, customer_address, raw_order, pizza_size, pizza_topping, play_audio = None, None, None, None, None, None, None

# --- Global Variables ---
# These hold the current session's state across multiple route requests.
# Reset to None on every visit to the home page to allow fresh orders.
language = None          # Watson TTS voice model selected by the customer
raw_address = None       # Raw STT transcript of the customer's delivery address
customer_address = None  # Cleaned version of raw_address (stopwords removed)
raw_order = None         # Raw STT transcript of the customer's pizza order
pizza_size = None        # Extracted pizza size from the order (e.g. ['Large'])
pizza_topping = None     # Extracted toppings from the order (e.g. ['Pepperoni', 'Mushroom'])
play_audio = None        # Filename of the current audio to stream to the front-end

@app.route("/")
def root():
    """ 
    Home page — resets all global state and deletes any leftover audio files
    from a previous session so the app is clean for a new order.
    """
      global language, raw_address, customer_address, raw_order, pizza_size, pizza_topping, play_audio
    language, raw_address, customer_address, raw_order, pizza_size, pizza_topping, play_audio = (
        None, None, None, None, None, None, None
    )
 
    # Clean up all audio files generated during a previous session
    files = [
        "info.wav", "info_record.wav", "info_repeat.wav",
        "topping.wav", "topping_record.wav", "topping_repeat.wav", "order.wav"
    ]
    for i in files:
        bash_command = str("find . -path \*/" + i + " -delete")
        os.system(bash_command)
 
    return render_template("main.html")
 
# --- Functional Pages ---
 
@app.route("/get_info", methods=["POST"])
def get_info():
    """
    Step 1 of ordering — greet the customer and ask for their delivery address.
    Saves the selected Watson voice language from the form and generates a welcome audio prompt.
    """
    global language, play_audio
 
    # Capture the voice/language selection from the HTML form (only set once per session)
    if not language:
        language = request.form["voice"]
 
    # Generate a TTS welcome message asking for the delivery address
    play_audio = "info.wav"
    result = "Welcome to La AI Pizza Plaza, how's it going? Where should we send your delicious pizza order to?"
    text_to_speech(result, play_audio, language)
 
    return render_template("getInfo.html")
 
@app.route("/get_topping", methods=["POST"])
def get_topping():
    """
    Step 2 of ordering — describe the pizza options and ask the customer to record their order.
    Generates a TTS prompt listing available sizes and toppings.
    """
    global play_audio
 
    play_audio = "topping.wav"
    result = (
        "At La AI Pizza Plaza, we offer a mouth-watering selection of giant, large, and medium pizzas, "
        "piled high with 8 delectable toppings to choose from. "
        "See the options in the picture below and indulge in the perfect pizza for you!"
    )
    text_to_speech(result, play_audio, language)
 
    return render_template("getTopping.html")
 
 
# --- Checking Pages ---
 
@app.route("/get_info_redirect", methods=["GET", "POST"])
def get_info_redirect():
    """
    Confirmation step for the delivery address.
    Cleans the raw STT transcript using clean_text(), then plays it back to the customer
    for confirmation. Passes the cleaned address to the HTML template for display.
    """
    global customer_address, play_audio
 
    # Strip stopwords from the raw address transcript for cleaner readback
    customer_address = clean_text(raw_address)
 
    play_audio = "info_repeat.wav"
    result = (
        "Just want to confirm, did ya ask for the pizza to be dropped off at " +
        customer_address +
        "? If not, no worries, just give the recording again button a tap."
    )
    text_to_speech(result, play_audio, language)
 
    # Pass customerAddress to the HTML template so it can be displayed on screen
    return render_template("getInfoRedirect.html", customerAddress=customer_address)
 
 
@app.route("/get_topping_redirect", methods=["GET", "POST"])
def get_topping_redirect():
    """
    Confirmation step for the pizza order.
    Cleans the raw order transcript, extracts size and toppings via get_keywords(),
    then reads the order back to the customer for confirmation.
    """
    global pizza_size, pizza_topping, play_audio
 
    # Clean stopwords from the raw order transcript
    clean_order = clean_text(raw_order)
 
    # Use fuzzy matching to extract pizza size and toppings from the cleaned text
    pizza_size, pizza_topping = get_keywords(clean_order)
 
    play_audio = "topping_repeat.wav"
    result = (
        "Just wanted to make sure, did ya order a " + pizza_size[0] +
        " pizza with: " + " ".join(map(str, pizza_topping)) +
        " on it? If not, no worries, just give the recording again button another press."
    )
    text_to_speech(result, play_audio, language)
 
    # Pass order details to the HTML template for display
    return render_template("getToppingRedirect.html", pizzaSize=pizza_size[0], pizzaTopping=pizza_topping)
 
 
# --- Result Page ---
 
@app.route("/get_order", methods=["POST"])
def get_order():
    """
    Final order confirmation page.
    Validates that all required order details are present, generates a full TTS order summary,
    and displays the complete order to the customer.
    """
    global play_audio
 
    play_audio = "order.wav"
 
    # Validate that all order components were captured before confirming
    if not customer_address:
        print("missing address")
    elif not pizza_size:
        print("missing pizza size")
    elif not pizza_topping:
        print("missing pizza topping")
 
    # Build and speak the full order confirmation message
    result = (
        "Thanks for using the La AI Pizza Plaza to place your order. "
        "Just wanted to double check that I got it right, ya want a " +
        pizza_size[0] + " pizza with " + " ".join(map(str, pizza_topping)) +
        ". And the delivery address is " + customer_address + ", is that correct?"
    )
    text_to_speech(result, play_audio, language)
 
    # Send all order details to the HTML template for final display
    return render_template(
        "getOrder.html",
        customerAddress=customer_address,
        orderSize=pizza_size[0],
        orderTopping=pizza_topping
    )
 
 
# --- Internal Audio Processing Routes ---
 
@app.route("/get_info_record_wav", methods=["POST"])
def get_info_record_wav():
    """
    Receives the customer's recorded address audio from the browser,
    saves it to disk, then transcribes it using Watson STT.
    The raw transcript is stored in raw_address for later cleaning.
    """
    global raw_address
 
    if "info_record_wav" not in request.files:
        return "No audio file found"
 
    file = request.files["info_record_wav"]
    if file.filename == "":
        return "No audio file selected"
 
    # Save the uploaded audio blob to disk so it can be sent to Watson STT
    save_audio(file, "info_record.wav")
 
    # Transcribe the saved audio and store the raw result
    raw_address = speech_to_text("info_record.wav")
    print("Raw address transcript:", raw_address)
 
    return render_template("getInfoRedirect.html")
 
 
@app.route("/get_topping_record_wav", methods=["POST"])
def get_topping_record_wav():
    """
    Receives the customer's recorded pizza order audio from the browser,
    saves it to disk, then transcribes it using Watson STT.
    The raw transcript is stored in raw_order for later cleaning and keyword extraction.
    """
    global raw_order
 
    if "topping_record_wav" not in request.files:
        return "No audio file found"
 
    file = request.files["topping_record_wav"]
    if file.filename == "":
        return "No audio file selected"
 
    # Save the uploaded audio blob and transcribe it
    save_audio(file, "topping_record.wav")
    raw_order = speech_to_text("topping_record.wav")
    print("Raw order transcript:", raw_order)
 
    return redirect("/get_topping_redirect")
 
 
@app.route("/play_local_wav")
def play_local_wav():
    """
    Streams the current play_audio .wav file back to the browser in real time.
    Uses a generator (play_local_wav_file) to send audio in 1024-byte chunks
    so it plays immediately without waiting for the full file to load.
    """
    return Response(play_local_wav_file(play_audio), mimetype="audio/x-wav")
 
 
if __name__ == "__main__":
    app.run(debug=True)
 