import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random
import time

st.title("🎂 Birthday Card Generator")

# Inputs
name = st.text_input("Enter Friend's Name")

style = st.selectbox(
    "Select Style",
    ["Fun", "Minimal", "Modern", "Friendship"]
)

# -------------------------------
# Text Generator (No API)
# -------------------------------
def generate_messages(name):
    templates = [
        f"Happy Birthday {name}! Wishing you lots of happiness and smiles. 🎉\nYour lovingly - Thanu",
        f"Hey {name}, hope your day is filled with joy and laughter! 🎂\nYour lovingly - Thanu",
        f"{name}, another year, more memories! Have a wonderful birthday! 🎈\nYour lovingly - Thanu",
        f"Happy Birthday {name}! Keep shining and smiling always 😊\nYour lovingly - Thanu",
        f"Dear {name}, wishing you a calm and beautiful year ahead 🌸\nYour lovingly - Thanu"
    ]
    return random.sample(templates, 3)

# -------------------------------
# Image Generator (Robust)
# -------------------------------
def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}"

    try:
        response = requests.get(url, timeout=10)

        # Check status
        if response.status_code != 200:
            return None

        # Check content type
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            return None

        return Image.open(BytesIO(response.content))

    except:
        return None

# -------------------------------
# Retry Wrapper
# -------------------------------
def get_image_with_retry(prompt, retries=3):
    for _ in range(retries):
        img = generate_image(prompt)
        if img:
            return img
        time.sleep(1)
    return None

# -------------------------------
# Card Creator
# -------------------------------
def create_card(image, text):
    image = image.resize((512, 512))

    card = Image.new("RGB", (512, 700), "white")
    card.paste(image, (0, 0))

    draw = ImageDraw.Draw(card)

    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    # Wrap text manually
    lines = []
    words = text.split()
    line = ""

    for word in words:
        if len(line + word) < 40:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    y_text = 530
    for line in lines:
        draw.text((20, y_text), line, fill="black", font=font)
        y_text += 25

    return card

# -------------------------------
# UI Action
# -------------------------------
if st.button("Generate Cards"):

    if not name:
        st.warning("Please enter a name")
    else:
        messages = generate_messages(name)

        for i, msg in enumerate(messages):
            st.subheader(f"🎉 Option {i+1}")

            prompt = f"high quality {style} birthday card for {name}, soft colors, clean design"

            img = get_image_with_retry(prompt)

            if img:
                st.image(img, caption="Generated Image")
            else:
                st.warning("⚠️ Image generation failed. Showing fallback.")
                img = Image.new("RGB", (512, 512), "lightblue")

            st.write(msg)

            # Create card
            card = create_card(img, msg)

            buf = BytesIO()
            card.save(buf, format="PNG")

            st.download_button(
                label="📥 Download Card",
                data=buf.getvalue(),
                file_name=f"{name}_card_{i+1}.png",
                mime="image/png"
            )
