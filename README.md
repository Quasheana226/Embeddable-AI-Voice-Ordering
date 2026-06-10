# 🍕 Embeddable AI Voice-Ordering — La AI Pizza Plaza

A voice-powered pizza ordering web app built with **IBM Watson AI** (Speech-to-Text, Text-to-Speech, and NLP) and **Flask**. Customers speak their delivery address and pizza order — Watson transcribes it, reads it back for confirmation, and displays the final order summary.

---

## Demo Flow

```
Home Page → Record Address → Confirm Address → Record Pizza Order → Confirm Order → Final Receipt
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| AI — Speech-to-Text | IBM Watson STT (Embeddable Library) |
| AI — Text-to-Speech | IBM Watson TTS (Embeddable Library) |
| NLP | NLTK stopwords + difflib fuzzy matching |
| Frontend | HTML5 / Bootstrap 4 / MediaRecorder API |
| Version Control | Git / GitHub |

---

## Project Structure

```
Embeddable-AI-Voice-Ordering/
│
├── app.py                  # Flask app — all routes and global state
├── helperFunctions.py      # Watson STT, TTS, NLP helpers
├── requirements.txt        # Python dependencies
│
├── templates/
│   ├── main.html           # Home — voice selector, start order
│   ├── getInfo.html        # Step 1 — record delivery address
│   ├── getInfoRedirect.html    # Confirm address Watson heard
│   ├── getTopping.html         # Step 2 — show menu, record order
│   ├── getToppingRedirect.html # Confirm size + toppings Watson heard
│   └── getOrder.html           # Final order receipt
│
└── static/
    ├── css/
    │   ├── bootstrap.css
    │   └── style.css       # Custom restaurant theme (gold #fac564)
    └── images/
        ├── bg_1.jpg                    # Hero background (ordering steps)
        ├── bg_4.jpg                    # Background (final receipt page)
        ├── food.png                    # Pizza menu / toppings image
        ├── sn_web.png                  # IBM Skills Network logo
        └── restaurant_map_location.png # Delivery area map
```

---

## Watson AI Endpoints

| Service | Endpoint |
|---|---|
| Speech-to-Text | `https://sn-watson-stt.labs.skills.network/speech-to-text/api/v1/recognize` |
| Text-to-Speech | `https://sn-watson-tts.labs.skills.network/text-to-speech/api/v1/synthesize` |

---

## Available Pizza Options

**Sizes:** Giant · Large · Medium

**Toppings:** Pepperoni · Bacon · Chicken · Anchovies · Mushroom · Onion · Black Olive · Green Pepper

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/Quasheana226/Embeddable-AI-Voice-Ordering.git
cd Embeddable-AI-Voice-Ordering
```

### 2. Install dependencies
```bash
pip install requests werkzeug==2.2.3 flask nltk --break-system-packages
```

### 3. Run the app
```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

> **Note:** Allow microphone access in your browser when prompted — the app records your voice using the MediaRecorder API.

---

## How It Works

1. **Home page** — customer selects a Watson TTS voice and clicks Start
2. **Watson TTS** speaks a greeting and asks for the delivery address
3. **Customer records** their address via browser mic (MediaRecorder API)
4. **Watson STT** transcribes the audio; NLTK removes filler words
5. **Watson TTS** reads the cleaned address back for confirmation
6. **Customer records** their pizza order (size + toppings)
7. **difflib fuzzy matching** extracts size and toppings from the transcript
8. **Watson TTS** reads the order back for confirmation
9. **Final page** displays the complete order summary with a delivery map

---

## Key Dependencies

| Package | Why |
|---|---|
| `flask` | Web framework — routes, templates, request handling |
| `requests` | HTTP calls to Watson STT/TTS APIs |
| `nltk` | Stopword removal to clean STT transcripts |
| `werkzeug==2.2.3` | Pinned to fix `url_quote` import error with Flask |
| `difflib` | Fuzzy string matching for pizza size/topping extraction |

---

## Good Commit Messages (Reference)

| Stage | Commit |
|---|---|
| Initial setup | `feat: scaffold Flask app and project structure` |
| STT added | `feat: integrate IBM Watson Speech-to-Text` |
| TTS added | `feat: integrate IBM Watson Text-to-Speech` |
| NLP added | `feat: add stopword cleaning and fuzzy keyword extraction` |
| Routes wired | `feat: connect Watson AI helpers to Flask routes` |
| Templates styled | `feat: add styled HTML templates using project images` |
| Bug fixes | `fix: guard against empty STT results and None globals` |

---

## Author

**Quasheana** — [GitHub @Quasheana226](https://github.com/Quasheana226)

Built as part of the IBM Skills Network — Embeddable AI lab.
