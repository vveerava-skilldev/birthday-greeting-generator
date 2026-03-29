import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import requests
from io import BytesIO
import random
import tempfile
import os

from gtts import gTTS
from pydub import AudioSegment

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

st.set_page_config(page_title="🎂 Birthday Studio", page_icon="🎂")

st.markdown("## 🎁 Personalized Birthday Song + Video Generator")
st.markdown("Enter a name → Get a custom song + video 🎶🎬")

# -------------------------------
# Inputs
# -------------------------------
name = st.text_input("Enter Name")

music_style = st.selectbox(
    "Music Style",
    ["Fun 🎉", "Emotional 💖", "Classic 🎼"]
)

# -------------------------------
# Music URLs (FREE)
# -------------------------------
MUSIC = {
    "Fun 🎉": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Emotional 💖": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Classic 🎼": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}

# -------------------------------
# GIF Backgrounds
# -------------------------------
GIFS = [
    "https://media.giphy.com/media/3o6ZtpxSZbQRRnwCKQ/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
]

def get_gif():
    return random.choice(GIFS)

# -------------------------------
# Lyrics Generator
# -------------------------------
def generate_lyrics(name, style):
    return f"""
🎶 Happy Birthday {name}! 🎶

Hey {name}, it's your special day,
Let's celebrate in a joyful way!
Clap your hands and sing out loud,
You're the brightest in the crowd!

Happy birthday to you,
All your dreams come true!
Keep shining every day,
In your own amazing way!

💖 From Thanu
"""

# -------------------------------
# Create Voice
# -------------------------------
def generate_voice(lyrics):
    tts = gTTS(text=lyrics, lang='en')

    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)

    return temp_audio.name

# -------------------------------
# Mix Audio
# -------------------------------
def mix_audio(voice_path, music_url):
    music_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    music_data = requests.get(music_url).content
    with open(music_file.name, "wb") as f:
        f.write(music_data)

    voice = AudioSegment.from_file(voice_path)
    music = AudioSegment.from_file(music_file.name)

    music = music - 18

    music = music * (len(voice) // len(music) + 1)
    music = music[:len(voice)]

    final_audio = voice.overlay(music)

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    final_audio.export(output.name, format="mp3")

    return output.name

# -------------------------------
# Create Frames
# -------------------------------
def create_frames(gif_url, text):
    response = requests.get(gif_url)
    gif = Image.open(BytesIO(response.content))

    frames = []

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        draw = ImageDraw.Draw(frame)

        draw.rectangle(
            [(20, frame.height-160), (frame.width-20, frame.height-20)],
            fill=(255,255,255,200)
        )

        y = frame.height - 150
        for line in text.split("\n"):
            w = draw.textlength(line, font=font)
            x = (frame.width - w) // 2
            draw.text((x, y), line, fill="black", font=font)
            y += 35

        frames.append(frame)

    return frames

# -------------------------------
# Create Video
# -------------------------------
def create_video(frames, audio_path):
    video_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_path = video_temp.name

    frame_list = [f.convert("RGB") for f in frames]

    clip = ImageSequenceClip(frame_list, fps=10)

    audio = AudioFileClip(audio_path).subclip(0, clip.duration)
    clip = clip.set_audio(audio)

    clip.write_videofile(
        video_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return video_path

# -------------------------------
# MAIN FLOW
# -------------------------------
if st.button("🎉 Generate Personalized Song + Video"):

    if not name:
        st.warning("Please enter a name")
    else:
        with st.spinner("✨ Creating your birthday magic..."):

            # Lyrics
            lyrics = generate_lyrics(name, music_style)
            st.text_area("🎶 Your Song", lyrics, height=200)

            # Voice
            voice_file = generate_voice(lyrics)

            # Mix audio
            final_audio = mix_audio(voice_file, MUSIC[music_style])
            st.audio(final_audio)

            # Frames
            gif_url = get_gif()
            frames = create_frames(gif_url, lyrics)
            st.image(frames[0], caption="🎨 Card Preview")

            # Video
            video_file = create_video(frames, final_audio)
            st.video(video_file)

            # Download
            with open(video_file, "rb") as f:
                st.download_button(
                    "📥 Download Birthday Video",
                    f,
                    file_name=f"{name}_birthday.mp4"
                )

            # Cleanup
            try:
                os.remove(video_file)
                os.remove(final_audio)
                os.remove(voice_file)
            except:
                pass

            st.success("🎉 Your personalized birthday video is ready!")
