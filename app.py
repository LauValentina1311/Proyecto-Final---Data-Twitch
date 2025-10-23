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
def main():
    try:
        data_limpia = load_and_clean_data("twitch_streamers.csv")
    except FileNotFoundError:
        st.error("Error: Asegúrate de que el archivo 'twitch_streamers.csv' esté en la misma carpeta que 'app.py'.")
        st.stop()

        #Generamos una Sidebar para la interacción dentro del Dashboard
        st.sidebar.header("Filtros Globales")
        selected_language = st.sidebar.multiselect(
            "Seleccionar Idioma(s) para el Análisis Detallado",
            options=data_limpia['LANGUAGE'].unique(),
            default=["English", "Spanish"]
        )

        #Filtro general aplicado al DataFrame
        df_filtered_lang = data_limpia[data_limpia['LANGUAGE'].isin(selected_language)]

        # --- Layout del Dashboard ---
        st.title("📊 Análisis Comparativo del Rendimiento de los Streamers de Twitch")
        st.markdown("---")

        #CONTENIDO DEL DASHBOARD

        #Verificación de datos
        if not df_filtered_lang.empty:

            #Análisis General de los Streamers
            st.header("5. Análisis General de los Streamers")

            #5.1 Conteo de Streamers por Región
            st.subheader("Conteo y Distribución General de Streamers")

            #Agrupación y conteo
            #Usamos data_limpia para el análisis general
            streamers_count = data_limpia['LANGUAGE'].value_counts().reset_index()
            streamers_count.columns = ['LANGUAGE', 'Número de Streamers']

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("### Tabla 1: Conteo de Streamers por Región")
                #Reemplazamos use_container_width=True por width='stretch'
                st.dataframe(streamers_count, width='stretch')
                st.markdown(f"""
                    **Análisis:** Se confirma el dominio de la comunidad **angloparlante (Inglés)** con **{streamers_count.iloc[0, 1]:,} streamers**. El español se posiciona como la tercera lengua más popular.
                    """)

            with col2:
                #Gráfico de barras
                fig_distribucion = px.bar(
                    streamers_count.sort_values(by='Número de Streamers', ascending=True),
                    x='Número de Streamers',
                    y='LANGUAGE',
                    orientation='h',
                    title="Distribución de Streamers por Región (Top 10)",
                    color_discrete_sequence=[PRIMARY_COLOR]
                )
                fig_distribucion.update_layout(yaxis={'title': 'Región'})
                #Reemplazamos use_container_width=True por width='stretch'
                st.plotly_chart(fig_distribucion, width='stretch')

            st.markdown("---")

        else:

            st.warning("Por favor, selecciona al menos un idioma en la barra lateral para ver el análisis detallado.")


    if __name__ == "__main__":
        main()