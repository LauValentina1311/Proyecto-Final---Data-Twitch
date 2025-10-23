import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuración de la Página de Streamlit
st.set_page_config(
    page_title="Dashboard de Streamers de Twitch",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definición de las Paletas de Colores
PALETTE_TWITCH = ["#6441a5", "#7f61bc", "#a690dd", "#b9baff", "#F0F0F0", "#000000"]
PALETTE_COLOURS = ["#6441a5", "#26C6DA", "#FF1493", "#FAFF00", "#5DFF00"]
PRIMARY_COLOR = PALETTE_COLOURS[0]


# Carga y limpieza de los datos
@st.cache_data
def load_and_clean_data(file_path):
    """Carga y limpia los datos de Twitch, asegurando que los idiomas estén en mayúsculas."""
    data = pd.read_csv(file_path)

    # Normalizar nombres de columnas a mayúsculas y quitar espacios extra
    data.columns = data.columns.str.strip().str.upper().str.replace(' ', '_')

    # *** AJUSTE CLAVE: Normalizar el contenido de la columna LANGUAGE a mayúsculas ***
    if 'LANGUAGE' in data.columns:
        data['LANGUAGE'] = data['LANGUAGE'].str.upper()

    # Lógica de limpieza: Buscar columna del segundo juego y reemplazar NA
    possible_cols = ['2ND_MOST_STREAMED_GAME', 'X2ND_MOST_STREAMED_GAME']
    target_col = None

    for col in possible_cols:
        if col.upper().replace(' ', '_') in data.columns:
            target_col = col.upper().replace(' ', '_')
            break

    if target_col:
        try:
            moda_streamed_game_2 = data[target_col].mode()[0]
            data = data.fillna({target_col: moda_streamed_game_2})
        except IndexError:
            data = data.fillna({target_col: 'No Game'})

    return data


# Función Principal de la Aplicación
def main():
    # Cargar los datos. Si falla, se muestra el error y la app se detiene.
    try:
        data_limpia = load_and_clean_data("twitch_streamers.csv")
        st.sidebar.success("✅ Datos cargados con éxito.")

    except FileNotFoundError:
        st.error("🔴 Error: Asegúrate de que el archivo 'twitch_streamers.csv' esté en la misma carpeta que 'app.py'.")
        return
    except Exception as e:
        st.error(f"🔴 Error inesperado durante la carga o limpieza de datos: {e}")
        return

    # --- 1. Generar Sidebar y Filtros ---
    st.sidebar.header("Filtros Globales")

    # Las opciones únicas ya estarán en mayúsculas gracias al cambio en load_and_clean_data
    language_options = data_limpia['LANGUAGE'].unique()

    # Usamos ENGLISH y SPANISH como default, que ahora coincidirán con las opciones.
    default_languages = [lang for lang in ["ENGLISH", "SPANISH"] if lang in language_options]

    selected_language = st.sidebar.multiselect(
        "Seleccionar Idioma(s) para el Análisis Detallado",
        options=language_options,
        default=default_languages
    )

    # Filtro general aplicado al DataFrame
    if selected_language:
        df_filtered_lang = data_limpia[data_limpia['LANGUAGE'].isin(selected_language)]
    else:
        df_filtered_lang = pd.DataFrame()

        # --- 2. Layout del Dashboard (Títulos Fijos) ---
    st.title("📊 Análisis Comparativo del Rendimiento de los Streamers de Twitch")
    st.markdown("---")

    # --- 3. CONTENIDO DEL DASHBOARD: SECCIÓN 5 (Análisis General) ---
    if not df_filtered_lang.empty:

        # 5. Análisis General de los Streamers
        st.header("5. Análisis General de los Streamers")

        # 5.1 Conteo de Streamers por Región
        st.subheader("Conteo y Distribución General de Streamers")

        # Agrupación y conteo (usando data_limpia para el análisis general)
        streamers_count = data_limpia['LANGUAGE'].value_counts().reset_index()
        streamers_count.columns = ['LANGUAGE', 'Número de Streamers']

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("### Tabla 1: Conteo de Streamers por Región")
            st.dataframe(streamers_count, width='stretch')

            english_count = streamers_count[streamers_count['LANGUAGE'] == 'ENGLISH']['Número de Streamers'].iloc[
                0] if 'ENGLISH' in streamers_count['LANGUAGE'].values else 0

            st.markdown(f"""
                **Análisis:** Se confirma el dominio de la comunidad **angloparlante (Inglés)** con **{english_count:,} streamers**. El español se posiciona como la tercera lengua más popular.
                """)

        with col2:
            # Gráfico de barras
            fig_distribucion = px.bar(
                streamers_count.sort_values(by='Número de Streamers', ascending=True),
                x='Número de Streamers',
                y='LANGUAGE',
                orientation='h',
                title="Distribución de Streamers por Región (Top 10)",
                color_discrete_sequence=[PRIMARY_COLOR]
            )
            fig_distribucion.update_layout(yaxis={'title': 'Región'})
            st.plotly_chart(fig_distribucion, width='stretch')

        st.markdown("---")

        # --- 4. CONTENIDO DEL DASHBOARD: SECCIÓN 6 (Análisis Detallado) ---

        st.header("6. Distribución de Categorías de Contenido por Región/Streamers")

        # 6.1 Top 5 Streamers por Followers
        st.subheader("6.1 Top 5 Streamers por Followers y Región")

        followers_region = df_filtered_lang.groupby(['LANGUAGE', 'NAME']).agg(
            TOTAL_FOLLOWERS=('TOTAL_FOLLOWERS', 'sum')
        ).reset_index()

        # Obtener el top 5 por idioma
        top_followers = followers_region.loc[
            followers_region.groupby('LANGUAGE')['TOTAL_FOLLOWERS'].nlargest(5).index.get_level_values(
                1)].sort_values(
            by=['LANGUAGE', 'TOTAL_FOLLOWERS'], ascending=[True, False]
        ).reset_index(drop=True)

        st.markdown("### Tabla 2: Top 5 Streamers por Followers y Región")
        st.dataframe(top_followers.style.format({'TOTAL_FOLLOWERS': '{:,.0f}'}), width='stretch')

        # Gráfico de barras
        fig_followers = px.bar(
            top_followers.sort_values(by='TOTAL_FOLLOWERS', ascending=True),
            x='TOTAL_FOLLOWERS',
            y='NAME',
            color='LANGUAGE',
            orientation='h',
            title="Top 5 Streamers por Followers y Región",
            labels={'TOTAL_FOLLOWERS': 'Total de Followers'},
            color_discrete_map={'ENGLISH': PALETTE_COLOURS[0], 'SPANISH': PALETTE_COLOURS[1]}
        )
        fig_followers.update_layout(xaxis_tickformat=',')
        st.plotly_chart(fig_followers, width='stretch')

        # Análisis de texto
        english_top = top_followers[top_followers['LANGUAGE'] == 'ENGLISH']
        spanish_top = top_followers[top_followers['LANGUAGE'] == 'SPANISH']

        analysis_text = "**Análisis:** "

        if not english_top.empty:
            analysis_text += f"El streamer con más seguidores en la comunidad angloparlante es **{english_top.iloc[0]['NAME']}** (con {english_top.iloc[0]['TOTAL_FOLLOWERS']:,.0f} seguidores). "

        if not spanish_top.empty:
            analysis_text += f"El streamer hispanohablante más popular es **{spanish_top.iloc[0]['NAME']}** (con {spanish_top.iloc[0]['TOTAL_FOLLOWERS']:,.0f} seguidores)."

        st.markdown(analysis_text)

        # 6.2 Top 5 Streamers por Views

        st.subheader("6.2 Top 5 Streamers por Views y Región")

        # Agrupación por media de views
        views_region = df_filtered_lang.groupby(['LANGUAGE', 'NAME']).agg(
            TOTAL_VIEWS=('TOTAL_VIEWS', 'mean')
        ).reset_index()

        # Obtener el top 5 por idioma
        top_views = views_region.loc[
            views_region.groupby('LANGUAGE')['TOTAL_VIEWS'].nlargest(5).index.get_level_values(1)].sort_values(
            by=['LANGUAGE', 'TOTAL_VIEWS'], ascending=[True, False]
        ).reset_index(drop=True)

        st.markdown("### Tabla 3: Top 5 Streamers por Views y Región (Media)")
        st.dataframe(top_views.style.format({'TOTAL_VIEWS': '{:,.0f}'}), width='stretch')

        # Gráfico de barras
        fig_views = px.bar(
            top_views.sort_values(by='TOTAL_VIEWS', ascending=True),
            x='TOTAL_VIEWS',
            y='NAME',
            color='LANGUAGE',
            orientation='h',
            title="Top 5 Streamers por Views y Región",
            labels={'TOTAL_VIEWS': 'Total de Views (Media)'},
            color_discrete_map={'ENGLISH': PALETTE_COLOURS[0], 'SPANISH': PALETTE_COLOURS[1]}
        )
        fig_views.update_layout(xaxis_tickformat=',')
        st.plotly_chart(fig_views, width='stretch')

        # Análisis para views
        english_views = top_views[top_views['LANGUAGE'] == 'ENGLISH']
        spanish_views = top_views[top_views['LANGUAGE'] == 'SPANISH']

        analysis_text_views = "**Análisis:** "

        if not english_views.empty:
            analysis_text_views += f"El streamer con más *views* de la comunidad angloparlante es **{english_views.iloc[0]['NAME']}** (con una media de {english_views.iloc[0]['TOTAL_VIEWS']:,.0f} views). "

        if not spanish_views.empty:
            analysis_text_views += f"El streamer hispanohablante más visto es **{spanish_views.iloc[0]['NAME']}** (con una media de {spanish_views.iloc[0]['TOTAL_VIEWS']:,.0f} views)."

        st.markdown(analysis_text_views)

        # 6.3 Top 5 Streamers por Juego más Streameado
        st.subheader("6.3 Top 5 Streamers por Juego más Streameado y Región")

        # Se obtienen los top 5 de cada idioma basado en TOTAL_FOLLOWERS
        juego_region = df_filtered_lang.sort_values(['LANGUAGE', 'TOTAL_FOLLOWERS'],
                                                    ascending=[True, False]).groupby('LANGUAGE').head(
            5).reset_index(drop=True)

        # Añadimos la columna de Rank
        juego_region['RANK_POR_IDIOMA'] = juego_region.groupby('LANGUAGE').cumcount() + 1

        juego_region_display = juego_region[
            ['RANK_POR_IDIOMA', 'LANGUAGE', 'NAME', 'MOST_STREAMED_GAME', 'TOTAL_FOLLOWERS']]

        st.markdown("### Tabla 4: Top 5 Streamers por Juego Más Streameado y Seguidores")
        st.dataframe(juego_region_display.style.format({'TOTAL_FOLLOWERS': '{:,.0f}'}),
                     width='stretch')

        # Gráfico de barras
        # Combinamos NAME y LANGUAGE para una mejor visualización del ranking
        juego_region['DISPLAY_NAME'] = juego_region['NAME'] + " (" + juego_region['LANGUAGE'] + " - Rank " + \
                                       juego_region['RANK_POR_IDIOMA'].astype(str) + ")"

        fig_juego = px.bar(
            juego_region.sort_values(by='TOTAL_FOLLOWERS', ascending=True),
            x='TOTAL_FOLLOWERS',
            y='DISPLAY_NAME',
            color='MOST_STREAMED_GAME',
            orientation='h',
            title="Top 5 Streamers por Juego Más Streameado",
            labels={'TOTAL_FOLLOWERS': 'Total de Followers', 'DISPLAY_NAME': 'Streamer y Región'},

            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_juego.update_layout(xaxis_tickformat=',')
        st.plotly_chart(fig_juego, width='stretch')

        st.markdown("""
        **Análisis:** La visualización interactiva confirma las tendencias. Por ejemplo, **Just Chatting** es una categoría clave en ambas comunidades. Puede interactuar con la leyenda de Plotly (haciendo clic en los juegos) para ver el impacto de cada categoría.
        """)
    else:
        st.warning("Por favor, selecciona al menos un idioma en la barra lateral para ver el análisis detallado.")


# Este bloque asegura que la función main se ejecute solo cuando el script se inicie
if __name__ == "__main__":
    main()