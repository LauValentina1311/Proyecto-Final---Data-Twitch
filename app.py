import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

#Configuración de la Página de Streamlit 
st.set_page_config(
    page_title="Dashboard de Streamers de Twitch",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Definición de las Paletas de Colores
PALETTE_TWITCH = ["#6441a5", "#7f61bc", "#a690dd", "#b9baff", "#F0F0F0", "#000000"]
PALETTE_COLOURS = ["#6441a5", "#26C6DA", "#FF1493", "#FAFF00", "#5DFF00"]
# Usaremos la primera paleta para consistencia en Plotly
PRIMARY_COLOR = PALETTE_COLOURS[0]

