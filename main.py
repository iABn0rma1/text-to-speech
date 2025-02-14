import re
from warnings import filterwarnings
filterwarnings("ignore")


from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


import soundfile as sf          # type: ignore
import numpy as np              # type: ignore
from kokoro import KPipeline    # type: ignore
import os


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


pipeline = KPipeline(lang_code='h')

def generate_audio(text: str, voice: str):
    try:
        text = re.sub(r'#(?=#|\s)|\*', '', text)

        voices = ["hf_alpha", "hf_beta"]
        if voice not in voices:
            raise ValueError(f"Voice must be one of {voices}")

        audio_clips = []
        generator = pipeline(text, voice=voice, speed=1, split_pattern=r'[.!?,\n]+')
        
        for _, _, audio in generator:
            audio_clips.append(audio)

        final_audio = np.concatenate(audio_clips)
        os.makedirs("static", exist_ok=True)
        filename = f"static/{voice}.wav"
        sf.write(filename, final_audio, 24000)
        
        return filename
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AudioRequest(BaseModel):
    text: str
    voice: str = "hf_beta"


@app.post("/generate-audio")
def generate_audio_endpoint(request: AudioRequest):
    filename = generate_audio(request.text, request.voice)
    return {"message": "Audio generated successfully", "filename": filename, "url": f"/static/{request.voice}.wav"}
