import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Streamlit 
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #ffe3ef 0%, #ffd6ea 45%, #fff0f7 100%);
}

h1, h2, h3 {
    color: #d63384;
}

section[data-testid="stSidebar"] {
    background: #fff0f7;
    border-right: 2px solid #f8b6d2;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #b02a6b;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    border-radius: 14px !important;
    border: 2px solid #f3a6c8 !important;
    background-color: white !important;
}

.stTextInput > div > div > input {
    border-radius: 14px;
}

.stButton > button {
    background: linear-gradient(135deg, #ff4fa3, #ff7bbf);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    box-shadow: 0 8px 20px rgba(255, 79, 163, 0.25);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #ff3d98, #ff69b4);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.canvas-card {
    background: rgba(255,255,255,0.72);
    border: 2px solid #f6b2d0;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 12px 30px rgba(214, 51, 132, 0.12);
    backdrop-filter: blur(10px);
}

.info-card {
    background: rgba(255,255,255,0.78);
    border: 2px solid #f6b2d0;
    border-radius: 20px;
    padding: 18px 20px;
    box-shadow: 0 10px 24px rgba(214, 51, 132, 0.10);
    margin-bottom: 16px;
}

.result-card {
    background: white;
    border: 2px solid #f3b3d1;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 10px 24px rgba(214, 51, 132, 0.10);
}

.small-note {
    color: #9c4674;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

st.title('Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de")
    st.write("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto.")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

st.markdown("""
<div class="info-card">
    <h3 style="margin-top:0;">Dibuja tu boceto</h3>
    <p class="small-note">Haz tu dibujo en el panel y luego presiona el botón para analizar la imagen.</p>
</div>
""", unsafe_allow_html=True)

drawing_mode = "freedraw"
stroke_color = "#000000"
bg_color = '#FFFFFF'

col1, col2, col3 = st.columns([1, 1.8, 1])

with col2:
    st.markdown('<div class="canvas-card">', unsafe_allow_html=True)

    canvas_result = st_canvas(
        fill_color="rgba(255, 105, 180, 0.18)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=300,
        width=400,
        drawing_mode=drawing_mode,
        key="canvas",
    )

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

colA, colB = st.columns([1.2, 1])

with colA:
    ke = st.text_input('Ingresa tu Clave', type="password")

with colB:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    analyze_button = st.button("Analiza la imagen", type="secondary", use_container_width=True)

os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe in spanish briefly the image"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            st.markdown('<div class="result-card">', unsafe_allow_html=True)

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
