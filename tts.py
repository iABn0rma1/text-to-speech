import re
from warnings import filterwarnings
filterwarnings("ignore")

from kokoro import KPipeline    # type: ignore
import soundfile as sf          # type: ignore
import numpy as np              # type: ignore

pipeline = KPipeline(lang_code='h')

def generate_audio(text, voice="hf_beta"):
    try:
        text = re.sub(r'#(?=#|\s)|\*', '', text)

        voices = [
            "hf_alpha", "hf_beta"
        ]
        if voice not in voices:
            raise ValueError(f"Voice must be one of {voices}")

        audio_clips = []

        # Generate audio for each voice
        generator = pipeline(
            text, voice=voice,
            speed=1, split_pattern=r'[.!?,\n]+'
        )
        for i, (gs, ps, audio) in enumerate(generator):
            audio_clips.append(audio)

        # Concatenate all segments into one
        final_audio = np.concatenate(audio_clips)

        # Save the final, combined file
        filename = f"{voice}.wav"
        sf.write(filename, final_audio, 24000)
        print(f"Saved {filename}")
        print("\n")

    except Exception as e:
        print(e)

text = """# Article on AI
महाकुंभ नगर मौनी से पहले ही दुनिया का सबसे अधिक आबादी वाला शहर बन गया। 
आज तीन सबसे अधिक जनसंख्या वाले शहरों की कुल आबादी को भी पार करने की संभावना है। 
दिल्ली से अधिक जापान की राजधानी टोक्यो की आबादी 3.74 करोड़ है। 
"""

generate_audio(text)