import pandas as pd
import streamlit as st

from utils.components import (
    content_card,
    kpi_card,
    page_header,
    render_sidebar,
    section_header,
)
from utils.data import (
    load_brand,
    load_category,
    load_club,
    load_province,
)
from utils.theme import (
    apply_theme,
    configure_page,
    SBL_BLUE,
    SUCCESS,
    WARNING,
)



configure_page(
    "Analisi territoriale dei club calcistici e dei brand sponsor"
)

apply_theme()
render_sidebar()


province_df = load_province()
club_df = load_club()
brand_df = load_brand()
category_df = load_category()



def find_column(dataframe, possible_names):
    """
    Restituisce il nome della prima colonna disponibile tra quelle indicate.
    Il confronto non distingue tra maiuscole e minuscole.
    """

    normalized_columns = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }

    for possible_name in possible_names:
        normalized_name = possible_name.strip().lower()

        if normalized_name in normalized_columns:
            return normalized_columns[normalized_name]

    return None


def count_unique_values(dataframe, possible_columns):
    """
    Conta i valori unici della prima colonna disponibile.
    Se nessuna colonna viene trovata, restituisce il numero di righe.
    """

    column = find_column(dataframe, possible_columns)

    if column is not None:
        return dataframe[column].dropna().nunique()

    return len(dataframe)


def format_integer(value):
    """
    Formatta un numero intero con il separatore italiano delle migliaia.
    """

    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "N/D"


def calculate_average(dataframe, possible_columns):
    """
    Calcola la media della prima colonna numerica disponibile.
    """

    column = find_column(dataframe, possible_columns)

    if column is None:
        return None

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return values.mean()


def format_decimal(value, decimals=1):
    """
    Formatta un numero decimale utilizzando la virgola.
    """

    if value is None or pd.isna(value):
        return "N/D"

    formatted_value = f"{value:,.{decimals}f}"

    return (
        formatted_value
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )



number_of_clubs = count_unique_values(
    club_df,
    [
        "club",
        "squadra",
        "team",
        "nome_club",
        "club_name",
    ],
)

number_of_provinces = count_unique_values(
    province_df,
    [
        "provincia",
        "den_prov",
        "nome_provincia",
        "province",
    ],
)

number_of_brands = count_unique_values(
    brand_df,
    [
        "brand",
        "sponsor",
        "brand_name",
        "nome_brand",
    ],
)

number_of_categories = count_unique_values(
    category_df,
    [
        "categoria",
        "category",
        "settore",
        "brand_category",
    ],
)

average_brand_power = calculate_average(
    brand_df,
    [
        "brand_power_index",
        "brand power index",
        "bpi",
        "power_index",
        "brand_power",
    ],
)



page_header(
    eyebrow="Dashboard territoriale",
    title=(
        "Analisi territoriale dei club calcistici "
        "e della forza dei brand sponsor in Italia"
    ),
    subtitle=(
        "Un’analisi provinciale della distribuzione dei club di Serie A "
        "e Serie B, della forza dei relativi sponsor e delle caratteristiche "
        "economiche e demografiche dei territori italiani."
    ),
)


content_card(
    title="Obiettivo dell’analisi",
    text=(
        "La dashboard integra dati relativi ai club di Serie A e Serie B, "
        "ai rispettivi sponsor e alle caratteristiche dei territori italiani. "
        "L’obiettivo è osservare congiuntamente la distribuzione geografica "
        "delle società calcistiche, la forza digitale e commerciale dei brand "
        "e il contesto economico e demografico delle province in cui tali "
        "relazioni si sviluppano."
    ),
)



section_header(
    title="Copertura dell’analisi",
    subtitle=(
        "Le principali dimensioni considerate nei dataset utilizzati "
        "per la costruzione della dashboard."
    ),
)

kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

with kpi_col_1:
    kpi_card(
        label="Club analizzati",
        value=format_integer(number_of_clubs),
        subtitle="Società appartenenti ai campionati di Serie A e Serie B.",
    )

with kpi_col_2:
    kpi_card(
        label="Province italiane",
        value=format_integer(number_of_provinces),
        subtitle="Territori provinciali inclusi nel dataset integrato.",
    )

with kpi_col_3:
    kpi_card(
        label="Brand sponsor",
        value=format_integer(number_of_brands),
        subtitle="Brand associati ai club e inclusi nell’analisi social.",
    )

with kpi_col_4:
    kpi_card(
        label="Categorie economiche",
        value=format_integer(number_of_categories),
        subtitle="Settori merceologici rappresentati dagli sponsor.",
    )




section_header(
    title="Esplora la dashboard",
    subtitle=(
        "Seleziona una sezione per accedere alle analisi e agli "
        "approfondimenti disponibili."
    ),
)


section_col_1, section_col_2, section_col_3 = st.columns(3)

with section_col_1:
    with st.container(border=True):
        st.caption("QUADRO GENERALE")
        st.markdown("### Panoramica nazionale")
        st.write(
            "Sintesi dei club, degli sponsor, delle categorie merceologiche "
            "e dei principali indicatori di Brand Power."
        )

        st.page_link(
            "pages/1_Panoramica_nazionale.py",
            label="Apri la panoramica nazionale",
            use_container_width=True,
        )

with section_col_2:
    with st.container(border=True):
        st.caption("CONFRONTO PROVINCIALE")
        st.markdown("### Analisi territoriale")
        st.write(
            "Confronto tra province attraverso indicatori demografici, "
            "economici, calcistici e commerciali."
        )

        st.page_link(
            "pages/2_Analisi_territoriale.py",
            label="Apri l’analisi territoriale",
            use_container_width=True,
        )

with section_col_3:
    with st.container(border=True):
        st.caption("RELAZIONI COMMERCIALI")
        st.markdown("### Club e Sponsor")
        st.write(
            "Analisi delle associazioni tra società calcistiche, sponsor, "
            "categorie economiche e Brand Power Index."
        )

        st.page_link(
            "pages/3_Brand_Sponsor.py",
            label="Apri Brand Sponsor",
            use_container_width=True,
        )


section_col_4, section_col_5, section_col_6 = st.columns(3)

with section_col_4:
    with st.container(border=True):
        st.caption("FOCUS TERRITORIALE")
        st.markdown("### Scheda provincia")
        st.write(
            "Approfondimento di una singola provincia attraverso dati "
            "demografici, economici, calcistici e commerciali."
        )

        st.page_link(
            "pages/4_Scheda_provincia.py",
            label="Apri la scheda provincia",
            use_container_width=True,
        )

with section_col_5:
    with st.container(border=True):
        st.caption("FOCUS SOCIETARIO")
        st.markdown("### Scheda club")
        st.write(
            "Profilo dettagliato di ciascun club, con localizzazione, "
            "sponsor e principali indicatori social."
        )

        st.page_link(
            "pages/5_Scheda_club.py",
            label="Apri la scheda club",
            use_container_width=True,
        )

with section_col_6:
    with st.container(border=True):
        st.caption("ESPLORAZIONE GEOGRAFICA")
        st.markdown("### Mappa interattiva")
        st.write(
            "Visualizzazione territoriale dei club, degli sponsor e degli "
            "indicatori provinciali attraverso la mappa Kepler."
        )

        st.page_link(
            "pages/6_Mappa_interattiva.py",
            label="Apri la mappa interattiva",
            use_container_width=True,
        )



section_header(
    title="Struttura dei dati",
    subtitle="Sintesi delle principali fonti informative integrate.",
)

data_col_1, data_col_2 = st.columns([1, 1])

with data_col_1:
    with st.container(border=True):
        st.markdown("#### Dimensione calcistica e commerciale")

        st.write(
            "I dataset dedicati ai club e agli sponsor comprendono "
            "informazioni relative alla categoria sportiva, alla provincia, "
            "al brand associato, al settore merceologico e agli indicatori "
            "di forza e presenza sui social media."
        )

with data_col_2:
    with st.container(border=True):
        st.markdown("#### Dimensione territoriale")

        st.write(
            "I dati provinciali integrano variabili demografiche, "
            "economiche e geografiche, consentendo di confrontare "
            "i territori e di interpretare la presenza dei club e degli "
            "sponsor nel relativo contesto locale."
        )




if average_brand_power is not None:
    st.info(
        "Il Brand Power Index medio dei brand inclusi nel dataset è pari a "
        f"{format_decimal(average_brand_power, decimals=2)}."
    )
    