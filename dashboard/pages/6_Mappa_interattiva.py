from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils.components import (
    page_header,
    render_sidebar,
    section_header,
)
from utils.theme import apply_theme, configure_page


configure_page("Mappa interattiva")

apply_theme()
render_sidebar()



PROJECT_ROOT = Path(__file__).resolve().parents[2]

SEARCH_DIRECTORIES = [
    PROJECT_ROOT / "outputs",
    PROJECT_ROOT / "dashboard" / "assets",
    PROJECT_ROOT / "data" / "processed",
    PROJECT_ROOT,
]


def find_kepler_maps():
    """
    Cerca i file HTML che potrebbero contenere la mappa Kepler.

    Vengono privilegiati i file il cui nome contiene:
    - kepler
    - mappa
    - map
    """

    preferred_keywords = [
        "kepler",
        "mappa",
        "map",
    ]

    discovered_files = []

    for directory in SEARCH_DIRECTORIES:
        if not directory.exists():
            continue

        for html_file in directory.rglob("*.html"):
            if html_file.is_file():
                discovered_files.append(html_file.resolve())

    discovered_files = list(dict.fromkeys(discovered_files))

    def priority(file_path):
        file_name = file_path.name.lower()

        keyword_priority = next(
            (
                index
                for index, keyword in enumerate(preferred_keywords)
                if keyword in file_name
            ),
            len(preferred_keywords),
        )

        return (
            keyword_priority,
            -file_path.stat().st_mtime,
        )

    return sorted(
        discovered_files,
        key=priority,
    )


def read_html_file(file_path):
    """Legge il contenuto della mappa HTML."""

    try:
        return file_path.read_text(
            encoding="utf-8",
        )

    except UnicodeDecodeError:
        return file_path.read_text(
            encoding="latin-1",
        )

    except OSError as error:
        st.error(
            "Non è stato possibile leggere il file della mappa.\n\n"
            f"Dettaglio: `{error}`"
        )
        return None


def format_file_size(file_path):
    """Formatta la dimensione del file HTML."""

    size_bytes = file_path.stat().st_size

    if size_bytes >= 1_000_000:
        return (
            f"{size_bytes / 1_000_000:.1f} MB"
            .replace(".", ",")
        )

    if size_bytes >= 1_000:
        return (
            f"{size_bytes / 1_000:.1f} KB"
            .replace(".", ",")
        )

    return f"{size_bytes} byte"


page_header(
    eyebrow="Esplorazione geografica",
    title="Mappa interattiva",
    subtitle=(
        "Esplora la distribuzione territoriale dei club calcistici, "
        "dei brand sponsor e degli indicatori provinciali attraverso "
        "la visualizzazione interattiva realizzata in Kepler.gl."
    ),
)


available_maps = find_kepler_maps()

if not available_maps:

    st.error(
        "Non è stato trovato alcun file HTML contenente la mappa."
    )

    with st.container(border=True):
        st.markdown("#### Dove inserire la mappa")

        st.write(
            "Esporta la visualizzazione da Kepler.gl come file HTML "
            "e salvala in una delle seguenti cartelle:"
        )

        for directory in SEARCH_DIRECTORIES[:3]:
            st.code(
                str(directory.relative_to(PROJECT_ROOT)),
                language=None,
            )

        st.write(
            "È consigliabile utilizzare un nome riconoscibile, "
            "ad esempio:"
        )

        st.code(
            "mappa_kepler_finale.html",
            language=None,
        )

    st.stop()



with st.container(border=True):
    st.markdown("#### Impostazioni di visualizzazione")

    control_col_1, control_col_2 = st.columns(
        [1.4, 0.6]
    )

    map_labels = {
        map_path.name: map_path
        for map_path in available_maps
    }

    with control_col_1:
        selected_map_name = st.selectbox(
            "File della mappa",
            options=list(map_labels.keys()),
            index=0,
            help=(
                "La dashboard seleziona automaticamente come prima opzione "
                "il file HTML più probabilmente associato a Kepler.gl."
            ),
        )

    with control_col_2:
        map_height = st.selectbox(
            "Altezza",
            options=[
                650,
                750,
                850,
                950,
            ],
            index=2,
            format_func=lambda value: f"{value} px",
        )


selected_map_path = map_labels[selected_map_name]




info_col_1, info_col_2, info_col_3 = st.columns(3)

with info_col_1:
    with st.container(border=True):
        st.metric(
            label="Formato",
            value="HTML",
        )
        st.caption("Mappa interattiva Kepler.gl.")


with info_col_3:
    with st.container(border=True):
        st.metric(
            label="Modalità",
            value="Interattiva",
        )
        st.caption("Zoom, filtri, livelli e tooltip disponibili.")


section_header(
    title="Esplora il territorio",
    subtitle=(
        "Utilizza i controlli interni alla mappa per attivare i livelli, "
        "modificare l’indicatore rappresentato, consultare la legenda "
        "e visualizzare i dettagli provinciali e societari."
    ),
)


map_html = read_html_file(selected_map_path)

if map_html is None:
    st.stop()

with st.container(border=True):

    components.html(
        map_html,
        height=map_height,
        scrolling=False,
    )


with st.expander(
    "Nota metodologica",
    expanded=False,
):
    st.write(
        "La componente territoriale integra i confini provinciali "
        "con indicatori demografici, economici, calcistici e commerciali. "
        "I marker rappresentano i club localizzati tramite le coordinate "
        "geografiche presenti nel dataset."
    )

    st.write(
        "Il GeoJSON provinciale è espresso nel sistema di riferimento "
        "EPSG:4326, compatibile con la visualizzazione web e con Kepler.gl."
    )

    st.write(
        "La mappa costituisce lo strumento conclusivo di esplorazione "
        "della dashboard e permette di approfondire spazialmente "
        "le evidenze illustrate nelle precedenti sezioni."
    )