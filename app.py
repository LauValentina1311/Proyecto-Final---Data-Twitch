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


#Carga y limpieza de los datos

#Usamos "@st.cache_data" para evitar recargar y limpiar los datos innecesariamente
@st.cache_data
def load_and_clean_data(file_path):
    """Carga y limpia los datos de Twitch"""
    data = pd.read_csv(file_path)

    #Limpieza de Datos
    #.mode()[0] toma el primer valor si hay múltiples modas o si la serie no está vacía
    moda_streamed_game_2 = data['2ND_MOST_STREAMED_GAME'].mode()[0]

    #Reemplazar valores NA (NaN) por la moda encontrada
    data_limpia = data.fillna({'2ND_MOST_STREAMED_GAME': moda_streamed_game_2})

    return data_limpia


# Cargar los datos limpios
try:
    data_limpia = load_and_clean_data("twitch_streamers.csv")
except FileNotFoundError:
    st.error("Error: Asegúrate de que el archivo 'twitch_streamers.csv' esté en la misma carpeta que 'app.py'.")
    st.stop()