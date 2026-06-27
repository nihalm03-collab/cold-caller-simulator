import io
import os
import time
import wave

import numpy as np
import requests
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()


ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
SARVAM_STT_URL = os.getenv("SARVAM_STT_URL", "https://api.sarvam.ai/speech-to-text")
CARTESIA_STT_URL = os.getenv("CARTESIA_STT_URL", "https://api.cartesia.ai/stt/transcribe")
CARTESIA_TTS_URL = os.getenv("CARTESIA_TTS_URL", "https://api.cartesia.ai/tts/bytes")


def _extract_transcript(payload: dict) -> str:
    """Extract transcript text from common STT response shapes."""
    transcript = (
        payload.get("transcript")
        or payload.get("text")
        or payload.get("result", {}).get("transcript")
        or payload.get("result", {}).get("text")
        or payload.get("data", {}).get("transcript")
        or payload.get("data", {}).get("text")
    )
    return str(transcript).strip() if transcript else ""


def _transcribe_with_sarvam(wav_bytes: bytes) -> str:
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("Missing SARVAM_API_KEY in .env")

    response = requests.post(
        SARVAM_STT_URL,
        headers={"api-subscription-key": api_key},
        files={"file": ("recording.wav", wav_bytes, "audio/wav")},
        data={
            "language_code": os.getenv("SARVAM_LANGUAGE_CODE", "hi-IN"),
            "model": os.getenv("SARVAM_STT_MODEL", "saarika:v2.5"),
        },
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()
    transcript = _extract_transcript(payload)
    if not transcript:
        raise RuntimeError(f"Sarvam STT response did not contain transcript: {payload}")

    return transcript


def _transcribe_with_cartesia(wav_bytes: bytes) -> str:
    api_key = os.getenv("CARTESIA_API_KEY")
    if not api_key:
        raise ValueError("Missing CARTESIA_API_KEY in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Cartesia-Version": os.getenv("CARTESIA_API_VERSION", "2024-06-10"),
    }
    response = requests.post(
        CARTESIA_STT_URL,
        headers=headers,
        files={"file": ("recording.wav", wav_bytes, "audio/wav")},
        data={
            "model": os.getenv("CARTESIA_STT_MODEL", "sonic-2"),
            "language": os.getenv("CARTESIA_LANGUAGE_CODE", "hi"),
        },
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()
    transcript = _extract_transcript(payload)
    if not transcript:
        raise RuntimeError(f"Cartesia STT response did not contain transcript: {payload}")

    return transcript


def _build_wav_bytes(samples: np.ndarray, sample_rate: int) -> bytes:
    """Convert mono float32 samples in range [-1, 1] to WAV bytes."""
    pcm16 = np.int16(np.clip(samples, -1.0, 1.0) * 32767)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm16.tobytes())
    return buffer.getvalue()


def _play_pcm(pcm_bytes: bytes, sample_rate: int = 16000) -> None:
    pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
    if pcm.size == 0:
        raise RuntimeError("TTS provider returned empty audio.")

    sd.play(pcm.astype(np.float32) / 32768.0, samplerate=sample_rate)
    sd.wait()


def _speak_with_elevenlabs(text: str) -> None:
    api_key = os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVEN_LABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")
    model_id = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

    if not api_key:
        raise ValueError("Missing ELEVENLABS_API_KEY (or ELEVEN_LABS_API_KEY) in .env")
    if not voice_id:
        raise ValueError("Missing ELEVENLABS_VOICE_ID in .env (set this to a Hindi male voice ID)")

    response = requests.post(
        ELEVENLABS_TTS_URL.format(voice_id=voice_id),
        params={"output_format": "pcm_16000"},
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/pcm",
        },
        json={
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        },
        timeout=60,
    )
    response.raise_for_status()
    _play_pcm(response.content, sample_rate=16000)


def _speak_with_cartesia(text: str) -> None:
    api_key = os.getenv("CARTESIA_API_KEY")
    if not api_key:
        raise ValueError("Missing CARTESIA_API_KEY in .env")

    voice_id = os.getenv("CARTESIA_VOICE_ID", "")
    if not voice_id:
        raise ValueError("Missing CARTESIA_VOICE_ID in .env")

    sample_rate = int(os.getenv("CARTESIA_TTS_SAMPLE_RATE", "16000"))
    payload = {
        "model_id": os.getenv("CARTESIA_TTS_MODEL", "sonic-latest"),
        "transcript": text,
        "voice": {"mode": "id", "id": voice_id},
        "language": os.getenv("CARTESIA_TTS_LANGUAGE", "hi"),
        "output_format": {
            "container": "raw",
            "encoding": "pcm_s16le",
            "sample_rate": sample_rate,
        },
    }
    response = requests.post(
        CARTESIA_TTS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Cartesia-Version": os.getenv("CARTESIA_API_VERSION", "2024-06-10"),
            "Content-Type": "application/json",
            "Accept": "application/octet-stream",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    _play_pcm(response.content, sample_rate=sample_rate)


def speak_text(text: str) -> None:
    """Send text to selected TTS provider and play audio immediately."""
    if not text or not text.strip():
        return

    provider = os.getenv("TTS_PROVIDER", "elevenlabs").strip().lower()
    if provider == "cartesia":
        _speak_with_cartesia(text)
        return

    _speak_with_elevenlabs(text)


def listen_speech() -> str:
    """Record up to 10 seconds (or until silence), send to STT, return transcript."""

    sample_rate = int(os.getenv("MIC_SAMPLE_RATE", "16000"))
    max_seconds = float(os.getenv("MIC_MAX_SECONDS", "10"))
    chunk_seconds = float(os.getenv("MIC_CHUNK_SECONDS", "0.2"))
    silence_threshold = float(os.getenv("MIC_SILENCE_THRESHOLD", "0.015"))
    silence_hold_seconds = float(os.getenv("MIC_SILENCE_HOLD", "1.2"))

    frames_per_chunk = max(1, int(sample_rate * chunk_seconds))
    chunks: list[np.ndarray] = []
    silent_for = 0.0
    min_recorded_before_stop = 0.8

    start_time = time.time()
    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        blocksize=frames_per_chunk,
    ) as stream:
        while (time.time() - start_time) < max_seconds:
            audio_block, _ = stream.read(frames_per_chunk)
            block = np.squeeze(audio_block)
            chunks.append(block.copy())

            rms = float(np.sqrt(np.mean(np.square(block)) + 1e-12))
            if rms < silence_threshold:
                silent_for += chunk_seconds
            else:
                silent_for = 0.0

            recorded_seconds = len(chunks) * chunk_seconds
            if recorded_seconds >= min_recorded_before_stop and silent_for >= silence_hold_seconds:
                break

    if not chunks:
        return ""

    audio = np.concatenate(chunks)
    wav_bytes = _build_wav_bytes(audio, sample_rate)

    provider = os.getenv("STT_PROVIDER", "sarvam").strip().lower()
    if provider == "cartesia":
        return _transcribe_with_cartesia(wav_bytes)

    return _transcribe_with_sarvam(wav_bytes)
