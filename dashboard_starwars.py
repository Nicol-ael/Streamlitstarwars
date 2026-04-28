# =============================================================================
# DASHBOARD GALACTICO: UNIVERSO STAR WARS
# Clase de Streamlit - Sesion 1 | Upgrade Hub Bootcamp
# =============================================================================
# Este archivo contiene una version completa del dashboard.
# La idea es que te sirva como repaso despues de la clase:
# - como configurar una app de Streamlit
# - como cargar un CSV con pandas
# - como crear filtros con widgets
# - como calcular KPIs
# - como construir graficos con Plotly
# - como mostrar tablas resumen
# =============================================================================

# Path permite construir rutas robustas entre archivos del proyecto.
# Asi evitamos depender del directorio desde el que se ejecute el comando.
from pathlib import Path

# Importamos Streamlit con el alias habitual "st".
# Todo lo que pintamos en pantalla sale de este modulo.
import streamlit as st

# pandas es la libreria principal para trabajar con tablas de datos.
import pandas as pd

# plotly.express permite crear graficos con pocas lineas.
# Lo importamos como "px", que es el alias mas usado en la practica.
import plotly.express as px


# =============================================================================
# BLOQUE 1 - CONFIGURACION DE LA PAGINA
# IMPORTANTE:
# st.set_page_config() debe aparecer antes de cualquier otro st.algo().
# Si llamas a Streamlit antes de esta funcion, la app puede dar error.
# =============================================================================
st.set_page_config(
    page_title="Dashboard Star Wars | Upgrade Hub",  # Titulo de la pestana del navegador.
    page_icon="*",  # Icono simple de la pestana. Usamos ASCII para evitar problemas de codificacion.
    layout="wide",  # "wide" aprovecha mejor el ancho de la pantalla.
    initial_sidebar_state="expanded",  # La barra lateral aparece abierta al iniciar.
)


# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# Streamlit permite inyectar CSS con st.markdown(..., unsafe_allow_html=True).
# Lo usamos para dar una estetica mas cinematografica a la app.
# =============================================================================
st.markdown(
    """
    <style>
        /* Fondo general de la aplicacion */
        .stApp {
            background: linear-gradient(180deg, #0a0a2e 0%, #1a1a3e 50%, #0a0a2e 100%);
        }

        /* Titulos principales en amarillo estilo Star Wars */
        h1, h2, h3 {
            color: #FFE81F !important;
        }

        /* Valor numerico grande dentro de st.metric() */
        [data-testid="stMetricValue"] {
            color: #FFE81F;
            font-size: 1.8rem;
        }

        /* Etiqueta de cada KPI */
        [data-testid="stMetricLabel"] {
            color: #CCCCCC;
        }

        /* Color de fondo de la barra lateral */
        [data-testid="stSidebar"] {
            background-color: #0d0d30;
        }
    </style>
    """,
    unsafe_allow_html=True,  # Necesario para que Streamlit interprete el HTML/CSS.
)


# Diccionario de colores para las facciones.
# Tener esta paleta en una sola variable ayuda a reutilizarla en todos los graficos.
COLORES_FACCION = {
    "Rebel Alliance": "#2196F3",  # Azul
    "Galactic Empire": "#F44336",  # Rojo
    "Jedi Order": "#4CAF50",  # Verde
    "Sith": "#9C27B0",  # Morado
    "Bounty Hunters": "#FF9800",  # Naranja
    "Neutral": "#9E9E9E",  # Gris
}

# Diccionario de colores para los sables laser.
COLORES_SABLE = {
    "Blue": "#4169E1",
    "Green": "#00CC00",
    "Red": "#FF0000",
    "Purple": "#9932CC",
    "White": "#F0F0F0",
    "Yellow": "#FFD700",
}


# =============================================================================
# BLOQUE 2 - CARGA DE DATOS
# Usamos @st.cache_data para que Streamlit guarde el resultado de la funcion.
# Ventaja:
# - la primera vez lee el CSV
# - en los siguientes reruns reutiliza el resultado
# Esto hace la app mas rapida cuando el usuario cambia filtros.
# =============================================================================
@st.cache_data
def cargar_datos():
    """Lee el CSV y devuelve un DataFrame listo para usar en la app."""

    # __file__ es la ruta del archivo .py actual.
    # with_name(...) sustituye solo el nombre final del archivo por el CSV.
    # Asi el codigo encuentra el dataset aunque el comando se ejecute desde otro sitio.
    ruta_csv = Path(__file__).with_name("starwars_characters.csv")

    # keep_default_na=False evita que textos vacios concretos se conviertan en NaN automaticamente.
    # Esto nos interesa para controlar nosotros mismos el valor de lightsaber_color.
    df = pd.read_csv(ruta_csv, keep_default_na=False)

    # Funcion auxiliar para convertir distintos formatos a booleano real.
    # Es util si algun dia el CSV trae "True"/"False" como texto.
    def a_bool(valor):
        # Si ya es booleano, lo devolvemos sin tocarlo.
        if isinstance(valor, bool):
            return valor

        # Normalizamos el valor:
        # - lo convertimos a texto
        # - quitamos espacios a izquierda y derecha
        # - pasamos todo a minusculas
        texto = str(valor).strip().lower()

        # Conjunto de textos que interpretaremos como True.
        if texto in {"true", "1", "yes", "si"}:
            return True

        # Conjunto de textos que interpretaremos como False.
        if texto in {"false", "0", "no", "", "none", "nan"}:
            return False

        # Si aparece un valor inesperado, lanzamos error para detectarlo pronto.
        raise ValueError(f"Valor booleano no reconocido: {valor!r}")

    # Aplicamos la conversion sobre toda la columna.
    # .apply() ejecuta la funcion elemento a elemento.
    df["force_sensitive"] = df["force_sensitive"].apply(a_bool)

    # Reemplazamos cadenas vacias por "None" para dejar claro que ese personaje no tiene sable.
    df["lightsaber_color"] = df["lightsaber_color"].replace("", "None")

    # Devolvemos el DataFrame ya limpio.
    return df


# Ejecutamos la funcion y guardamos el resultado en la variable principal del dashboard.
df = cargar_datos()


# =============================================================================
# BLOQUE 3 - CABECERA DE LA APP
# =============================================================================
st.title("Dashboard Galactico: Universo Star Wars")  # Titulo grande principal.
st.markdown(
    "Explora los datos de **65 personajes** del universo Star Wars. "
    "Usa los filtros del panel lateral para descubrir patrones en la galaxia."
)  # Texto enriquecido en Markdown; **...** pone negrita.
st.caption("Clase de Streamlit - Sesion 1 | Upgrade Hub Bootcamp")  # Texto pequeno de apoyo.


# =============================================================================
# BLOQUE 4 - SIDEBAR CON FILTROS
# Todo lo que se escribe dentro de with st.sidebar: aparece en la barra lateral.
# Cada widget devuelve un valor que guardamos en una variable.
# =============================================================================
with st.sidebar:
    # Titulo del panel lateral.
    st.header("Panel de Control")

    # Linea horizontal de separacion.
    st.markdown("---")

    # ------------------------------
    # FILTRO 1 - FACCION
    # ------------------------------
    # .unique() devuelve los valores distintos de la columna.
    # .tolist() los convierte a lista de Python.
    # sorted(...) los ordena alfabeticamente.
    facciones_disponibles = sorted(df["allegiance"].unique().tolist())

    # st.multiselect permite elegir varias opciones.
    facciones = st.multiselect(
        "Faccion",  # Etiqueta que ve el usuario.
        options=facciones_disponibles,  # Lista completa de opciones posibles.
        default=facciones_disponibles,  # Estado inicial: todas seleccionadas.
        help="Selecciona una o varias facciones para filtrar",  # Tooltip de ayuda.
    )

    # ------------------------------
    # FILTRO 2 - ERA
    # ------------------------------
    eras_disponibles = sorted(df["era"].unique().tolist())
    eras = st.multiselect(
        "Era",
        options=eras_disponibles,
        default=eras_disponibles,
    )

    # Nuevo separador visual.
    st.markdown("---")

    # ------------------------------
    # FILTRO 3 - ESPECIE
    # ------------------------------
    # Anadimos manualmente la opcion "Todas" para representar "sin filtro".
    especies_disponibles = ["Todas"] + sorted(df["species"].unique().tolist())

    # st.selectbox obliga a elegir una unica opcion.
    especie = st.selectbox(
        "Especie",  # Etiqueta del selector.
        options=especies_disponibles,  # Opciones del desplegable.
    )

    # ------------------------------
    # FILTRO 4 - ALTURA
    # ------------------------------
    # Convertimos a int para evitar valores numpy y tener enteros limpios en el slider.
    altura_min = int(df["height_cm"].min())
    altura_max = int(df["height_cm"].max())

    # Si pasamos una tupla en value=(min, max), st.slider crea un rango.
    rango_altura = st.slider(
        "Rango de altura (cm)",  # Etiqueta del widget.
        min_value=altura_min,  # Limite inferior permitido.
        max_value=altura_max,  # Limite superior permitido.
        value=(altura_min, altura_max),  # Valor inicial del rango.
    )

    # ------------------------------
    # FILTRO 5 - SOLO FUERZA
    # ------------------------------
    # st.checkbox devuelve True cuando esta marcado y False cuando no.
    solo_fuerza = st.checkbox("Solo sensibles a la Fuerza")

    # ------------------------------
    # FILTRO 6 - POPULARIDAD MINIMA
    # ------------------------------
    min_popularidad = st.slider(
        "Rating minimo de popularidad",
        min_value=1.0,  # Valor minimo permitido.
        max_value=5.0,  # Valor maximo permitido.
        value=1.0,  # Valor inicial.
        step=0.5,  # Incremento de medio punto en medio punto.
    )

    # Otro separador visual.
    st.markdown("---")

    # ------------------------------
    # FILTRO 7 - BUSQUEDA POR NOMBRE
    # ------------------------------
    busqueda = st.text_input(
        "Buscar personaje por nombre",
        placeholder="Ej: Skywalker",  # Texto gris que aparece antes de escribir.
    ).strip()  # .strip() elimina espacios sobrantes al principio y al final.


# =============================================================================
# BLOQUE 5 - LOGICA DE FILTRADO
# Creamos una copia del DataFrame original y aplicamos los filtros uno a uno.
# Trabajar sobre una copia evita tocar el DataFrame base.
# =============================================================================
df_filtrado = df.copy()

# Filtro por faccion.
# .isin(lista) devuelve True en las filas cuyo valor pertenece a la lista.
df_filtrado = df_filtrado[df_filtrado["allegiance"].isin(facciones)]

# Filtro por era.
df_filtrado = df_filtrado[df_filtrado["era"].isin(eras)]

# Filtro por especie.
# Solo se aplica si la opcion elegida no es "Todas".
if especie != "Todas":
    df_filtrado = df_filtrado[df_filtrado["species"] == especie]

# Filtro por rango de altura.
# Combinamos dos condiciones con &:
# - altura mayor o igual al minimo
# - altura menor o igual al maximo
df_filtrado = df_filtrado[
    (df_filtrado["height_cm"] >= rango_altura[0])
    & (df_filtrado["height_cm"] <= rango_altura[1])
]

# Filtro por sensibilidad a la Fuerza.
# Solo se activa cuando el checkbox esta marcado.
if solo_fuerza:
    df_filtrado = df_filtrado[df_filtrado["force_sensitive"]]

# Filtro por popularidad minima.
df_filtrado = df_filtrado[df_filtrado["popularity_rating"] >= min_popularidad]

# Filtro por busqueda textual.
# str.contains(...) busca coincidencias dentro del texto.
# case=False ignora mayusculas/minusculas.
# na=False evita errores si hubiera valores faltantes.
if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado["name"].str.contains(busqueda, case=False, na=False)
    ]

# Si no queda ninguna fila, mostramos aviso y detenemos la app con st.stop().
if df_filtrado.empty:
    st.warning("No se encontraron personajes con estos filtros. Prueba a cambiarlos.")
    st.stop()


# =============================================================================
# BLOQUE 6 - KPIS PRINCIPALES
# st.columns(4) crea 4 columnas del mismo ancho.
# Dentro de cada columna mostramos un KPI con st.metric().
# =============================================================================
col1, col2, col3, col4 = st.columns(4)

# Calculamos metricas base a partir del DataFrame filtrado.
total_personajes = len(df_filtrado)  # Numero de filas visibles.
altura_media = df_filtrado["height_cm"].mean()  # Media de altura en centimetros.
pct_fuerza = (df_filtrado["force_sensitive"].sum() / total_personajes) * 100  # Porcentaje de True.
total_bounty = df_filtrado["credits_bounty"].sum()  # Suma total de recompensas.

col1.metric(
    "Total Personajes",  # Etiqueta del KPI.
    f"{total_personajes}",  # Valor principal.
    delta=f"de {len(df)} en total",  # Texto secundario comparativo.
)
col2.metric(
    "Altura Media",
    f"{altura_media:.0f} cm",  # :.0f redondea a 0 decimales.
)
col3.metric(
    "% Sensibles a la Fuerza",
    f"{pct_fuerza:.1f}%",  # :.1f muestra 1 decimal.
)
col4.metric(
    "Total Recompensas",
    f"{total_bounty:,.0f} creditos",  # :, inserta separador de miles.
)

# Separamos la fila de KPIs del resto del contenido.
st.markdown("---")


# =============================================================================
# BLOQUE 7 - TABS
# st.tabs(...) crea pestanas.
# Cada variable (tab1, tab2, tab3) representa una pestana distinta.
# =============================================================================
tab1, tab2, tab3 = st.tabs(
    [
        "Vista General",
        "Graficos Detallados",
        "Tabla de Datos",
    ]
)


# =============================================================================
# TAB 1 - VISTA GENERAL
# =============================================================================
with tab1:
    # Creamos dos columnas con proporcion 2:1.
    # La izquierda ocupara el doble de espacio que la derecha.
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.subheader("Distribucion por Faccion")

        # value_counts() cuenta cuantas veces aparece cada categoria.
        # reset_index() convierte el resultado en DataFrame.
        conteo_facciones = df_filtrado["allegiance"].value_counts().reset_index()

        # Renombramos las columnas resultantes para trabajar mas comodamente.
        conteo_facciones.columns = ["allegiance", "count"]

        # Grafico de barras.
        fig_facciones = px.bar(
            conteo_facciones,  # DataFrame fuente.
            x="allegiance",  # Variable del eje X.
            y="count",  # Variable del eje Y.
            color="allegiance",  # Coloreamos cada barra segun la faccion.
            color_discrete_map=COLORES_FACCION,  # Mapa fijo de colores.
            template="plotly_dark",  # Tema oscuro de Plotly.
            labels={  # Texto mas legible en ejes y tooltips.
                "allegiance": "Faccion",
                "count": "Personajes",
            },
        )

        # No hace falta leyenda porque las categorias ya aparecen en el eje X.
        fig_facciones.update_layout(showlegend=False)

        # width="stretch" hace que el grafico ocupe todo el ancho disponible.
        st.plotly_chart(fig_facciones, width="stretch")

    with col_der:
        st.subheader("Sensibilidad a la Fuerza")

        # Traducimos True / False a etiquetas mas amigables.
        conteo_fuerza = (
            df_filtrado["force_sensitive"]
            .map({True: "Sensible", False: "No sensible"})
            .value_counts()
            .reset_index()
        )
        conteo_fuerza.columns = ["force_sensitive", "count"]

        # Grafico circular tipo donut.
        fig_fuerza = px.pie(
            conteo_fuerza,
            names="force_sensitive",  # Categoria que divide el pastel.
            values="count",  # Valor numerico que determina el tamano.
            color="force_sensitive",  # Coloreamos cada segmento por categoria.
            color_discrete_map={
                "Sensible": "#00BCD4",
                "No sensible": "#607D8B",
            },
            hole=0.4,  # hole crea el agujero central del donut.
            template="plotly_dark",
        )
        st.plotly_chart(fig_fuerza, width="stretch")

    # Expander: seccion que se puede abrir y cerrar.
    with st.expander("Top 10 guerreros por batallas"):
        # nlargest(10, ...) devuelve las 10 filas con mayor valor en esa columna.
        top_guerreros = df_filtrado.nlargest(10, "battles_fought")[
            ["name", "allegiance", "battles_fought", "victories"]
        ]

        fig_top = px.bar(
            top_guerreros,
            x="battles_fought",
            y="name",
            color="allegiance",
            color_discrete_map=COLORES_FACCION,
            orientation="h",  # "h" crea barras horizontales.
            template="plotly_dark",
            labels={
                "battles_fought": "Batallas",
                "name": "",
                "allegiance": "Faccion",
            },
        )

        # categoryorder ordena las barras por valor total en el eje Y.
        fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top, width="stretch")


# =============================================================================
# TAB 2 - GRAFICOS DETALLADOS
# =============================================================================
with tab2:
    col_izq2, col_der2 = st.columns(2)

    with col_izq2:
        st.subheader("Altura vs Midi-chlorians")

        # Para este scatter solo tienen sentido los personajes con midi_chlorians > 0.
        df_fuerza = df_filtrado[df_filtrado["midi_chlorians"] > 0]

        if not df_fuerza.empty:
            fig_scatter = px.scatter(
                df_fuerza,
                x="height_cm",  # Eje horizontal.
                y="midi_chlorians",  # Eje vertical.
                color="allegiance",  # Color segun faccion.
                size="battles_fought",  # Tamano del punto segun numero de batallas.
                hover_name="name",  # Nombre mostrado al pasar el raton.
                color_discrete_map=COLORES_FACCION,
                template="plotly_dark",
                labels={
                    "height_cm": "Altura (cm)",
                    "midi_chlorians": "Midi-chlorians",
                    "allegiance": "Faccion",
                    "battles_fought": "Batallas",
                },
            )
            st.plotly_chart(fig_scatter, width="stretch")
        else:
            # st.info muestra una caja informativa azul.
            st.info("No hay personajes sensibles a la Fuerza con los filtros actuales.")

    with col_der2:
        st.subheader("Colores de Sable Laser")

        # Excluimos los personajes cuyo valor es "None".
        df_sables = df_filtrado[df_filtrado["lightsaber_color"] != "None"]

        if not df_sables.empty:
            conteo_sables = df_sables["lightsaber_color"].value_counts().reset_index()
            conteo_sables.columns = ["lightsaber_color", "count"]

            fig_sables = px.pie(
                conteo_sables,
                names="lightsaber_color",
                values="count",
                color="lightsaber_color",
                color_discrete_map=COLORES_SABLE,
                template="plotly_dark",
            )
            st.plotly_chart(fig_sables, width="stretch")
        else:
            st.info("No hay personajes con sable laser con los filtros actuales.")

    st.subheader("Top 15 por Victorias")

    top_victorias = df_filtrado.nlargest(15, "victories")[
        ["name", "allegiance", "victories", "battles_fought"]
    ]

    fig_victorias = px.bar(
        top_victorias,
        x="victories",
        y="name",
        color="allegiance",
        color_discrete_map=COLORES_FACCION,
        orientation="h",
        template="plotly_dark",
        labels={
            "victories": "Victorias",
            "name": "",
            "allegiance": "Faccion",
        },
    )
    fig_victorias.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_victorias, width="stretch")

    with st.expander("Distribucion de Popularidad"):
        fig_hist = px.histogram(
            df_filtrado,
            x="popularity_rating",  # Variable numerica que queremos distribuir.
            color="era",  # Desglosamos el histograma por era.
            nbins=10,  # Numero de barras o intervalos.
            template="plotly_dark",
            labels={
                "popularity_rating": "Rating de Popularidad",
                "era": "Era",
                "count": "Personajes",
            },
        )
        st.plotly_chart(fig_hist, width="stretch")


# =============================================================================
# TAB 3 - TABLAS
# =============================================================================
with tab3:
    st.subheader("Datos Filtrados")

    # st.dataframe crea una tabla interactiva:
    # - se puede ordenar
    # - se puede hacer scroll
    # - se adapta mejor que st.table para muchos datos
    st.dataframe(
        df_filtrado,
        width="stretch",  # Ocupa todo el ancho del contenedor.
        hide_index=True,  # Oculta el indice numerico de pandas.
    )

    # Dos columnas para mostrar dos tablas resumen lado a lado.
    col_tabla1, col_tabla2 = st.columns(2)

    with col_tabla1:
        st.subheader("Resumen por Faccion")

        # groupby(...) agrupa las filas por categoria.
        # agg(...) define que calculo hacemos en cada nueva columna.
        resumen_faccion = (
            df_filtrado.groupby("allegiance")
            .agg(
                personajes=("name", "count"),  # Cuenta nombres por faccion.
                altura_media=("height_cm", "mean"),  # Media de altura.
                batallas_media=("battles_fought", "mean"),  # Media de batallas.
            )
            .round(1)  # Redondea los numeros a 1 decimal.
        )
        st.dataframe(resumen_faccion, width="stretch")

    with col_tabla2:
        st.subheader("Resumen por Era")

        resumen_era = (
            df_filtrado.groupby("era")
            .agg(
                personajes=("name", "count"),
                popularidad_media=("popularity_rating", "mean"),
                total_bounty=("credits_bounty", "sum"),
            )
            .round(1)
        )
        st.dataframe(resumen_era, width="stretch")


# =============================================================================
# BLOQUE 8 - FOOTER
# =============================================================================
st.markdown("---")
st.caption("Dashboard creado en la clase de Streamlit | Upgrade Hub Bootcamp")
st.success("Que la Fuerza te acompane en tu camino como data analyst.")
