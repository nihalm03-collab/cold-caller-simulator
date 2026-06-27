# AI Cold Caller Simulator

An AI-powered voice simulator that lets you practice cold sales calls against a realistic, skeptical procurement persona. Speak into your microphone, and the AI responds in real time with human-like voice — helping sales reps sharpen their pitch, handle objections, and build confidence before real calls.

---

## How It Works

The simulator runs a continuous **STT → LLM → TTS** pipeline:

1. **STT (Speech-to-Text):** Your spoken input is captured from the microphone and transcribed to text using the Sarvam AI API (`saarika:v2.5`), with silence detection to automatically stop recording.
2. **LLM (Language Model):** The transcript is appended to the full conversation history and sent to Google Gemini (`gemini-2.5-flash`), which responds in character as Raj Sharma — a skeptical procurement manager based in Pune who speaks Hinglish, raises real objections, and only agrees to a demo if the pitch is convincing.
3. **TTS (Text-to-Speech):** Raj's reply is converted to natural-sounding speech using the Cartesia TTS API and played back immediately through your speakers.

The full conversation is also printed to the terminal as a live transcript.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| LLM | Google Gemini (`google-generativeai`) |
| TTS | Cartesia / ElevenLabs |
| STT | Sarvam AI |
| Audio I/O | `sounddevice`, `numpy` |
| Env management | `python-dotenv` |
| Orchestration | LangChain |
| *(planned)* API server | FastAPI |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/nihalm03-collab/cold-caller-simulator.git
cd cold-caller-simulator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is not yet generated, install manually:
> ```bash
> pip install google-generativeai python-dotenv requests numpy sounddevice
> ```

### 3. Configure environment variables

Copy or create a `.env` file in the project root and fill in your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

CARTESIA_API_KEY=your_cartesia_api_key_here
CARTESIA_VOICE_ID=your_cartesia_hindi_male_voice_id_here
CARTESIA_TTS_MODEL=sonic-latest
CARTESIA_TTS_LANGUAGE=hi
CARTESIA_TTS_SAMPLE_RATE=16000
CARTESIA_API_VERSION=2024-06-10
TTS_PROVIDER=cartesia

SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saarika:v2.5
SARVAM_LANGUAGE_CODE=hi-IN
STT_PROVIDER=sarvam
```

### 4. Run the simulator

```bash
python main.py
```

Speak when you see `Listening...`. Say **"quit"** or **"bye"** to end the session.

---

## Demo

> 🎥 **Demo video:** _coming soon_
>
> <!-- Replace the line below with your actual demo link -->
> [Watch Demo](https://your-demo-link-here)
