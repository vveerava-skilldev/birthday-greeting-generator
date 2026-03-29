import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import requests
from io import BytesIO
import random

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="🎂 Pro Birthday Cards", page_icon="🎂")

st.title("🎂 Pro Animated Birthday Card Generator")

# -------------------------------
# Inputs
# -------------------------------
name = st.text_input("Enter Friend's Name")

theme = st.selectbox(
    "Choose Theme",
    ["Floral 🌸", "Party 🎈", "Elegant ✨", "Minimal 🎁"]
)

mode = st.radio(
    "Message Mode",
    ["🧠 Auto Generate", "🎨 Custom Message"]
)

custom_msg = ""
if mode == "🎨 Custom Message":
    custom_msg = st.text_area("Enter your custom birthday message")

# -------------------------------
# GIF Backgrounds
# -------------------------------
GIFS = [
    "https://media.giphy.com/media/3o6ZtpxSZbQRRnwCKQ/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif"
]

def get_gif():
    return random.choice(GIFS)

# -------------------------------
# Smart Message Generator
# -------------------------------
def smart_generate_messages(name, theme):
    openers = [
        f"Happy Birthday {name}!",
        f"Hey {name}!",
        f"Dear {name},",
        f"Cheers to you {name}!"
    ]

    vibes = {
        "Floral 🌸": [
            "May your day bloom with happiness",
            "Wishing you a day full of peace and beauty"
        ],
        "Party 🎈": [
            "Let’s celebrate big today",
            "Time to enjoy, laugh and party"
        ],
        "Elegant ✨": [
            "Wishing you grace and happiness always",
            "May your journey be bright and meaningful"
        ],
        "Minimal 🎁": [
            "Simple moments, big happiness",
            "Stay happy, stay you"
        ]
    }

    closings = [
        "Keep shining always",
        "Have an amazing year ahead",
        "Enjoy your special day",
        "Stay happy and blessed"
    ]

    signature = "💖 Your lovingly - Thanu"

    messages = []

    for _ in range(3):
        msg = f"{random.choice(openers)}\n" \
              f"{random.choice(vibes[theme])}.\n" \
              f"{random.choice(closings)}.\n\n{signature}"

        messages.append(msg)

    return messages

# -------------------------------
# Decorations
# -------------------------------
def draw_decor(draw, frame, theme):
    w, h = frame.size

    if "Floral" in theme:
        for _ in range(15):
            draw.text((random.randint(0,w), random.randint(0,h)), "🌸", fill="pink")

    elif "Party" in theme:
        for _ in range(10):
            draw.text((random.randint(0,w), random.randint(0,h)), "🎈", fill="red")
        for _ in range(15):
            draw.text((random.randint(0,w), random.randint(0,h)), "🎊", fill="yellow")

    elif "Elegant" in theme:
        for _ in range(10):
            draw.text((random.randint(0,w), random.randint(0,h)), "✨", fill="white")

    elif "Minimal" in theme:
        for _ in range(10):
            draw.ellipse(
                (random.randint(0,w), random.randint(0,h),
                 random.randint(0,w)+3, random.randint(0,h)+3),
                fill="gray"
            )

# -------------------------------
# Create Animated Card
# -------------------------------
def create_card(gif_url, text, theme):
    response = requests.get(gif_url)
    gif = Image.open(BytesIO(response.content))

    frames = []

    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
        text_font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")

        # Overlay box
        overlay = Image.new("RGBA", frame.size, (0,0,0,0))
        o_draw = ImageDraw.Draw(overlay)
        o_draw.rectangle(
            [(20, frame.height-160), (frame.width-20, frame.height-20)],
            fill=(255,255,255,210)
        )

        frame = Image.alpha_composite(frame, overlay)
        draw = ImageDraw.Draw(frame)

        # Decorations
        draw_decor(draw, frame, theme)

        # Text
        lines = text.split("\n")
        y = frame.height - 150

        for i, line in enumerate(lines):
            font = title_font if i == 0 else text_font

            text_width = draw.textlength(line, font=font)
            x = (frame.width - text_width) // 2

            # glow
            draw.text((x-1,y-1), line, fill="gray", font=font)
            draw.text((x+1,y+1), line, fill="gray", font=font)

            draw.text((x,y), line, fill="black", font=font)
            y += 30

        frames.append(frame.convert("P"))

    buf = BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=gif.info.get("duration", 100),
        loop=0
    )

    buf.seek(0)
    return buf

# -------------------------------
# Generate Button
# -------------------------------
if st.button("🚀 Generate Cards"):

    if not name:
        st.warning("Please enter a name")
    else:
        if mode == "🎨 Custom Message" and custom_msg:
            messages = [custom_msg]
        else:
            messages = smart_generate_messages(name, theme)

        for i, msg in enumerate(messages):
            st.subheader(f"🎉 Option {i+1}")

            gif_url = get_gif()
            st.image(gif_url, caption="🎬 Preview")

            card = create_card(gif_url, msg, theme)

            st.image(card, caption="🎨 Final Animated Card")

            st.download_button(
                "📥 Download",
                data=card,
                file_name=f"{name}_card_{i+1}.gif",
                mime="image/gif"
            )
