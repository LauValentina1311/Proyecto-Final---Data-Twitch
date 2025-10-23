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

        #Distribución de Categorías de Contenido por Región

        st.header("6. Distribución de Categorías de Contenido por Región/Streamers")

        #6.1 Top 5 Streamers por Followers

        st.subheader("6.1 Top 5 Streamers por Followers y Región")
        if not df_filtered_lang.empty:
            followers_region = df_filtered_lang.groupby(['LANGUAGE', 'NAME']).agg(
                TOTAL_FOLLOWERS=('TOTAL_FOLLOWERS', 'sum')
            ).reset_index()

            #Obtener el top 5 por idioma
            top_followers = followers_region.loc[
                followers_region.groupby('LANGUAGE')['TOTAL_FOLLOWERS'].nlargest(5).index.get_level_values(
                    1)].sort_values(
                by=['LANGUAGE', 'TOTAL_FOLLOWERS'], ascending=[True, False]
            ).reset_index(drop=True)

            st.markdown("### Tabla 2: Top 5 Streamers por Followers y Región")
            #Muestra la tabla de seguidores
            st.dataframe(top_followers.style.format({'TOTAL_FOLLOWERS': '{:,.0f}'}), use_container_width=True)

            #Gráfico de barras
            fig_followers = px.bar(
                top_followers.sort_values(by='TOTAL_FOLLOWERS', ascending=True),
                x='TOTAL_FOLLOWERS',
                y='NAME',
                color='LANGUAGE',
                orientation='h',
                title="Top 5 Streamers por Followers y Región",
                labels={'TOTAL_FOLLOWERS': 'Total de Followers'},
                color_discrete_map={'English': PALETTE_COLOURS[0], 'Spanish': PALETTE_COLOURS[1]}
            )
            fig_followers.update_layout(xaxis_tickformat=',')
            st.plotly_chart(fig_followers, use_container_width=True)

            st.markdown(f"""
            **Análisis:** El streamer con más seguidores en la comunidad angloparlante es **{top_followers[top_followers['LANGUAGE'] == 'English'].iloc[0]['NAME']}** (con {top_followers[top_followers['LANGUAGE'] == 'English'].iloc[0]['TOTAL_FOLLOWERS']:,.0f} seguidores). El streamer hispanohablante más popular es **{top_followers[top_followers['LANGUAGE'] == 'Spanish'].iloc[0]['NAME']}** (con {top_followers[top_followers['LANGUAGE'] == 'Spanish'].iloc[0]['TOTAL_FOLLOWERS']:,.0f} seguidores).
            """)
        else:
            st.warning("Selecciona al menos un idioma en la barra lateral para ver este análisis.")

            #6.2 Top 5 Streamers por Views

            st.subheader("6.2 Top 5 Streamers por Views y Región")

            if not df_filtered_lang.empty:
                #Agrupación por media de views
                views_region = df_filtered_lang.groupby(['LANGUAGE', 'NAME']).agg(
                    TOTAL_VIEWS=('TOTAL_VIEWS', 'mean')
                ).reset_index()

                #Obtener el top 5 por idioma
                top_views = views_region.loc[
                    views_region.groupby('LANGUAGE')['TOTAL_VIEWS'].nlargest(5).index.get_level_values(1)].sort_values(
                    by=['LANGUAGE', 'TOTAL_VIEWS'], ascending=[True, False]
                ).reset_index(drop=True)

                st.markdown("### Tabla 3: Top 5 Streamers por Views y Región (Media)")
                st.dataframe(top_views.style.format({'TOTAL_VIEWS': '{:,.0f}'}), use_container_width=True)

                #Gráfico de barras 
                fig_views = px.bar(
                    top_views.sort_values(by='TOTAL_VIEWS', ascending=True),
                    x='TOTAL_VIEWS',
                    y='NAME',
                    color='LANGUAGE',
                    orientation='h',
                    title="Top 5 Streamers por Views y Región",
                    labels={'TOTAL_VIEWS': 'Total de Views (Media)'},
                    color_discrete_map={'English': PALETTE_COLOURS[0], 'Spanish': PALETTE_COLOURS[1]}
                )
                fig_views.update_layout(xaxis_tickformat=',')
                st.plotly_chart(fig_views, use_container_width=True)

                st.markdown(f"""
                **Análisis:** El streamer con más *views* de la comunidad angloparlante es **{top_views[top_views['LANGUAGE'] == 'English'].iloc[0]['NAME']}** (con una media de {top_views[top_views['LANGUAGE'] == 'English'].iloc[0]['TOTAL_VIEWS']:,.0f} views). El streamer hispanohablante más visto es **{top_views[top_views['LANGUAGE'] == 'Spanish'].iloc[0]['NAME']}** (con una media de {top_views[top_views['LANGUAGE'] == 'Spanish'].iloc[0]['TOTAL_VIEWS']:,.0f} views).
                """)
            else:
                st.warning("Selecciona al menos un idioma en la barra lateral para ver este análisis.")