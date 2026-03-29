import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random

st.title("🎂 Birthday Card Generator")

# Inputs
name = st.text_input("Enter Friend's Name")

style = st.selectbox(
    "Select Style",
    ["Fun", "Minimal", "Modern", "Friendship"]
)

# Simple text generator (no API)
def generate_messages(name):
    templates = [
        f"Happy Birthday {name}! Wishing you lots of happiness and smiles. 🎉\nYour lovingly - Thanu",
        f"Hey {name}, hope your day is filled with joy and laughter! 🎂\nYour lovingly - Thanu",
        f"{name}, another year, more memories! Have a wonderful birthday! 🎈\nYour lovingly - Thanu",
        f"Happy Birthday {name}! Keep shining and smiling always 😊\nYour lovingly - Thanu",
        f"Dear {name}, wishing you a calm and beautiful year ahead 🌸\nYour lovingly - Thanu"
    ]
    return random.sample(templates, 3)

# Generate Image from Pollinations
def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Create card image
def create_card(image, text):
    image = image.resize((512, 512))
    card = Image.new("RGB", (512, 700), "white")
    card.paste(image, (0, 0))

    draw = ImageDraw.Draw(card)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw.text((20, 530), text, fill="black", font=font)

    return card

# Button action
if st.button("Generate Cards"):

    if not name:
        st.warning("Please enter a name")
    else:
        messages = generate_messages(name)

        for i, msg in enumerate(messages):
            st.subheader(f"🎉 Option {i+1}")

            # Image prompt
            prompt = f"{style} birthday card for {name}, soft colors, friendship theme"

            img = generate_image(prompt)
            st.image(img, caption="Generated Image")

            st.write(msg)

            # Create downloadable card
            card = create_card(img, msg)

            buf = BytesIO()
            card.save(buf, format="PNG")

            st.download_button(
                label="📥 Download Card",
                data=buf.getvalue(),
                file_name=f"{name}_birthday_card_{i+1}.png",
                mime="image/png"
            )
