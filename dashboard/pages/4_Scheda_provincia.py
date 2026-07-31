from pathlib import Path
from urllib.parse import quote

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.components import (
    kpi_card,
    page_header,
    render_sidebar,
    section_header,
)
from utils.data import load_club, load_province
from utils.theme import apply_theme, configure_page


# ==========================================================
# Configurazione della pagina
# ==========================================================

configure_page("Scheda provincia")

apply_theme()
render_sidebar()


# ==========================================================
# Impostazioni grafiche
# ==========================================================

PRIMARY_BLUE = "#173F56"
SECONDARY_BLUE = "#2C6E91"
LIGHT_BLUE = "#8FB9CE"
VERY_LIGHT_BLUE = "#DCEAF1"
DARK_GREY = "#46545E"
LIGHT_GREY = "#E8EDF0"

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}


# ==========================================================
# Percorsi
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROVINCE_GEOJSON_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "province_master_finale.geojson"
)


# ==========================================================
# Caricamento dati
# ==========================================================

province_df = load_province().copy()
club_df = load_club().copy()

if not PROVINCE_GEOJSON_PATH.exists():
    st.error(
        "Il file GeoJSON delle province non è stato trovato nel percorso:\n\n"
        f"`{PROVINCE_GEOJSON_PATH}`"
    )
    st.stop()

province_geo = gpd.read_file(PROVINCE_GEOJSON_PATH)


# ==========================================================
# Pulizia dei dati
# ==========================================================

province_text_columns = [
    "provincia",
    "regione",
    "sigla_provincia",
    "club_presenti",
]

province_numeric_columns = [
    "numero_comuni",
    "numero_contribuenti",
    "reddito_complessivo_euro",
    "reddito_medio_provinciale_euro",
    "numero_club",
    "serie_a",
    "serie_b",
    "popolazione_residente",
    "pop_15_34",
    "perc_15_34",
    "pop_over65",
    "perc_over65",
    "eta_media",
    "club_per_100k",
    "numero_brand_sponsor",
    "brand_power_index",
]

club_text_columns = [
    "club",
    "lega",
    "città",
    "provincia",
    "sigla (provincia)",
    "regione",
]

club_numeric_columns = [
    "lat",
    "long",
    "brand_power_index",
    "numero_brand_sponsor",
]

geo_text_columns = [
    "provincia",
    "regione",
    "sigla_provincia",
]

for column in province_text_columns:
    if column in province_df.columns:
        province_df[column] = (
            province_df[column]
            .astype("string")
            .str.strip()
        )

for column in province_numeric_columns:
    if column in province_df.columns:
        province_df[column] = pd.to_numeric(
            province_df[column],
            errors="coerce",
        )

for column in club_text_columns:
    if column in club_df.columns:
        club_df[column] = (
            club_df[column]
            .astype("string")
            .str.strip()
        )

for column in club_numeric_columns:
    if column in club_df.columns:
        club_df[column] = pd.to_numeric(
            club_df[column],
            errors="coerce",
        )

for column in geo_text_columns:
    if column in province_geo.columns:
        province_geo[column] = (
            province_geo[column]
            .astype("string")
            .str.strip()
        )

if province_geo.crs is None:
    province_geo = province_geo.set_crs("EPSG:4326")

elif province_geo.crs.to_epsg() != 4326:
    province_geo = province_geo.to_crs("EPSG:4326")


# ==========================================================
# Funzioni di supporto
# ==========================================================

def format_integer(value):
    """Formatta un numero intero secondo la convenzione italiana."""

    if pd.isna(value):
        return "N/D"

    return f"{int(round(value)):,}".replace(",", ".")


def format_decimal(value, decimals=2):
    """Formatta un numero decimale con la virgola."""

    if pd.isna(value):
        return "N/D"

    formatted_value = f"{value:,.{decimals}f}"

    return (
        formatted_value
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )


def format_currency(value):
    """Formatta un valore monetario in euro."""

    if pd.isna(value):
        return "N/D"

    return f"€ {format_integer(value)}"


def safe_value(row, column):
    """Restituisce il valore di una colonna o NaN se non disponibile."""

    if column not in row.index:
        return float("nan")

    return row[column]


def percentile_rank(series, value):
    """
    Calcola la posizione percentile di un valore rispetto
    alla distribuzione nazionale.
    """

    clean_series = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    if clean_series.empty or pd.isna(value):
        return float("nan")

    return float((clean_series <= value).mean() * 100)


def national_rank(series, value, ascending=False):
    """
    Restituisce la posizione nazionale del valore.
    In caso di valori uguali assegna lo stesso ranking minimo.
    """

    clean_series = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    if clean_series.empty or pd.isna(value):
        return None

    ranked_series = clean_series.rank(
        method="min",
        ascending=ascending,
    )

    matching_indices = clean_series[
        clean_series == value
    ].index

    if len(matching_indices) == 0:
        return None

    return int(ranked_series.loc[matching_indices].min())


def normalize_against_national(series, value):
    """
    Trasforma il valore in percentile nazionale da 0 a 100.
    È utilizzato nel radar comparativo.
    """

    return percentile_rank(series, value)


def get_query_province():
    """Legge la provincia eventualmente presente nell’URL."""

    query_value = st.query_params.get("provincia")

    if isinstance(query_value, list):
        query_value = query_value[0] if query_value else None

    if query_value is None:
        return None

    query_value = str(query_value).strip()

    available_provinces = (
        province_df["provincia"]
        .dropna()
        .astype(str)
        .tolist()
    )

    matching_province = next(
        (
            province
            for province in available_provinces
            if province.casefold() == query_value.casefold()
        ),
        None,
    )

    return matching_province


def update_query_province(province_name):
    """Aggiorna il parametro provincia nell’URL."""

    current_value = st.query_params.get("provincia")

    if isinstance(current_value, list):
        current_value = current_value[0] if current_value else None

    if current_value != province_name:
        st.query_params["provincia"] = province_name


def calculate_map_zoom(geometry):
    """Stima uno zoom adeguato in base all’estensione della provincia."""

    min_x, min_y, max_x, max_y = geometry.total_bounds

    longitude_span = max_x - min_x
    latitude_span = max_y - min_y
    maximum_span = max(longitude_span, latitude_span)

    if maximum_span < 0.25:
        return 9.1

    if maximum_span < 0.50:
        return 8.4

    if maximum_span < 0.90:
        return 7.8

    if maximum_span < 1.50:
        return 7.1

    return 6.5


def apply_standard_layout(
    figure,
    title=None,
    height=440,
    show_legend=False,
):
    """Applica lo stile comune ai grafici Plotly."""

    figure.update_layout(
        title={
            "text": title,
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 18,
                "color": PRIMARY_BLUE,
            },
        }
        if title
        else None,
        height=height,
        margin={
            "l": 30,
            "r": 30,
            "t": 65 if title else 30,
            "b": 40,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": "Arial",
            "color": DARK_GREY,
        },
        showlegend=show_legend,
        hoverlabel={
            "bgcolor": "white",
            "font_size": 13,
        },
    )

    return figure


# ==========================================================
# Provincia iniziale da URL
# ==========================================================

query_province = get_query_province()

if query_province is not None:
    query_region = province_df.loc[
        province_df["provincia"] == query_province,
        "regione",
    ].iloc[0]
else:
    query_region = None


# ==========================================================
# Header
# ==========================================================

page_header(
    eyebrow="Approfondimento territoriale",
    title="Scheda provincia",
    subtitle=(
        "Profilo interattivo delle province italiane con indicatori "
        "demografici, economici, calcistici e commerciali, confronto "
        "con il quadro nazionale e localizzazione dei club presenti."
    ),
)


# ==========================================================
# Selettori
# ==========================================================

with st.container(border=True):
    st.markdown("#### Seleziona il territorio")

    filter_col_1, filter_col_2 = st.columns(2)

    available_regions = sorted(
        province_df["regione"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    default_region_index = 0

    if query_region in available_regions:
        default_region_index = available_regions.index(query_region)

    with filter_col_1:
        selected_region = st.selectbox(
            "Regione",
            options=available_regions,
            index=default_region_index,
        )

    available_provinces = sorted(
        province_df.loc[
            province_df["regione"] == selected_region,
            "provincia",
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    default_province_index = 0

    if (
        query_province in available_provinces
        and query_region == selected_region
    ):
        default_province_index = available_provinces.index(
            query_province
        )

    with filter_col_2:
        selected_province = st.selectbox(
            "Provincia",
            options=available_provinces,
            index=default_province_index,
        )


update_query_province(selected_province)


# ==========================================================
# Estrazione dei dati della provincia
# ==========================================================

province_rows = province_df[
    province_df["provincia"] == selected_province
]

if province_rows.empty:
    st.error(
        "La provincia selezionata non è presente nel dataset."
    )
    st.stop()

province_row = province_rows.iloc[0]

selected_geo = province_geo[
    province_geo["provincia"] == selected_province
].copy()

selected_clubs = club_df[
    club_df["provincia"] == selected_province
].copy()


# ==========================================================
# Intestazione dinamica
# ==========================================================

with st.container(border=True):

    title_col, summary_col = st.columns([1.5, 1])

    with title_col:
        st.caption("PROVINCIA SELEZIONATA")
        st.title(selected_province)
        st.write(selected_region)

    with summary_col:
        st.metric(
            label="Club presenti",
            value=format_integer(
                safe_value(
                    province_row,
                    "numero_club",
                )
            ),
        )

        club_names = (
            selected_clubs["club"]
            .dropna()
            .astype(str)
            .tolist()
        )

        if club_names:
            st.caption(", ".join(club_names))
        else:
            st.caption(
                "Nessun club di Serie A o Serie B presente."
            )


# ==========================================================
# KPI principali
# ==========================================================

section_header(
    title="Profilo provinciale",
    subtitle=(
        "Principali indicatori economici, demografici, calcistici "
        "e commerciali del territorio selezionato."
    ),
)

kpi_row_1 = st.columns(3)

with kpi_row_1[0]:
    kpi_card(
        label="Popolazione residente",
        value=format_integer(
            safe_value(
                province_row,
                "popolazione_residente",
            )
        ),
        subtitle=(
            f"{format_integer(safe_value(province_row, 'numero_comuni'))} "
            "comuni inclusi."
        ),
    )

with kpi_row_1[1]:
    kpi_card(
        label="Reddito medio",
        value=format_currency(
            safe_value(
                province_row,
                "reddito_medio_provinciale_euro",
            )
        ),
        subtitle="Reddito medio provinciale per contribuente.",
    )

with kpi_row_1[2]:
    kpi_card(
        label="Età media",
        value=(
            f"{format_decimal(safe_value(province_row, 'eta_media'), 1)} "
            "anni"
        ),
        subtitle=(
            f"15-34 anni: "
            f"{format_decimal(safe_value(province_row, 'perc_15_34'), 1)}%."
        ),
    )


kpi_row_2 = st.columns(3)

with kpi_row_2[0]:
    kpi_card(
        label="Numero di club",
        value=format_integer(
            safe_value(
                province_row,
                "numero_club",
            )
        ),
        subtitle=(
            f"Serie A: {format_integer(safe_value(province_row, 'serie_a'))} "
            f"— Serie B: {format_integer(safe_value(province_row, 'serie_b'))}."
        ),
    )

with kpi_row_2[1]:
    kpi_card(
        label="Club ogni 100.000 abitanti",
        value=format_decimal(
            safe_value(
                province_row,
                "club_per_100k",
            ),
            3,
        ),
        subtitle="Indicatore di intensità calcistica provinciale.",
    )

with kpi_row_2[2]:
    kpi_card(
        label="Brand sponsor",
        value=format_integer(
            safe_value(
                province_row,
                "numero_brand_sponsor",
            )
        ),
        subtitle=(
            "Brand Power Index: "
            f"{format_decimal(safe_value(province_row, 'brand_power_index'), 3)}."
        ),
    )


# ==========================================================
# Radar e confronto nazionale
# ==========================================================

section_header(
    title="Posizionamento rispetto al quadro nazionale",
    subtitle=(
        "Gli indicatori sono convertiti in percentile nazionale: "
        "un valore più elevato indica un posizionamento superiore "
        "rispetto alle altre province."
    ),
)

comparison_col_1, comparison_col_2 = st.columns([1.25, 0.75])


# ----------------------------------------------------------
# Radar provinciale
# ----------------------------------------------------------

with comparison_col_1:
    with st.container(border=True):

        radar_indicators = [
            {
                "label": "Reddito medio",
                "column": "reddito_medio_provinciale_euro",
            },
            {
                "label": "Popolazione",
                "column": "popolazione_residente",
            },
            {
                "label": "Club / 100k",
                "column": "club_per_100k",
            },
            {
                "label": "Giovani 15-34",
                "column": "perc_15_34",
            },
            {
                "label": "Brand sponsor",
                "column": "numero_brand_sponsor",
            },
            {
                "label": "Brand Power",
                "column": "brand_power_index",
            },
        ]

        radar_labels = []
        radar_values = []

        for indicator in radar_indicators:
            column = indicator["column"]
            value = safe_value(province_row, column)

            if (
                column in province_df.columns
                and not pd.isna(value)
            ):
                radar_labels.append(indicator["label"])
                radar_values.append(
                    normalize_against_national(
                        province_df[column],
                        value,
                    )
                )

        if len(radar_values) >= 3:

            closed_labels = radar_labels + [radar_labels[0]]
            closed_values = radar_values + [radar_values[0]]

            radar_figure = go.Figure()

            radar_figure.add_trace(
                go.Scatterpolar(
                    r=closed_values,
                    theta=closed_labels,
                    fill="toself",
                    name=selected_province,
                    line={
                        "color": PRIMARY_BLUE,
                        "width": 3,
                    },
                    fillcolor="rgba(23, 63, 86, 0.20)",
                    hovertemplate=(
                        "<b>%{theta}</b><br>"
                        "Percentile nazionale: %{r:.1f}"
                        "<extra></extra>"
                    ),
                )
            )

            radar_figure.add_trace(
                go.Scatterpolar(
                    r=[50] * len(closed_labels),
                    theta=closed_labels,
                    name="Mediana nazionale",
                    mode="lines",
                    line={
                        "color": LIGHT_BLUE,
                        "width": 2,
                        "dash": "dash",
                    },
                    hoverinfo="skip",
                )
            )

            radar_figure.update_layout(
                polar={
                    "radialaxis": {
                        "visible": True,
                        "range": [0, 100],
                        "ticksuffix": "° pct.",
                        "gridcolor": LIGHT_GREY,
                    },
                    "angularaxis": {
                        "gridcolor": LIGHT_GREY,
                    },
                    "bgcolor": "rgba(0,0,0,0)",
                },
                legend={
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": 1.05,
                    "xanchor": "left",
                    "x": 0,
                },
            )

            radar_figure = apply_standard_layout(
                radar_figure,
                title="Profilo relativo della provincia",
                height=500,
                show_legend=True,
            )

            st.plotly_chart(
                radar_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili abbastanza indicatori "
                "per costruire il profilo comparativo."
            )


# ----------------------------------------------------------
# Ranking nazionale
# ----------------------------------------------------------

with comparison_col_2:
    with st.container(border=True):

        st.markdown("#### Posizione nazionale")

        ranking_definitions = [
            {
                "label": "Reddito medio",
                "column": "reddito_medio_provinciale_euro",
                "ascending": False,
            },
            {
                "label": "Popolazione",
                "column": "popolazione_residente",
                "ascending": False,
            },
            {
                "label": "Club ogni 100.000",
                "column": "club_per_100k",
                "ascending": False,
            },
            {
                "label": "Quota 15-34 anni",
                "column": "perc_15_34",
                "ascending": False,
            },
            {
                "label": "Brand Power Index",
                "column": "brand_power_index",
                "ascending": False,
            },
        ]

        available_rankings = 0

        for ranking_definition in ranking_definitions:

            column = ranking_definition["column"]
            value = safe_value(province_row, column)

            if (
                column not in province_df.columns
                or pd.isna(value)
            ):
                continue

            ranking = national_rank(
                province_df[column],
                value,
                ascending=ranking_definition["ascending"],
            )

            valid_count = province_df[column].notna().sum()

            if ranking is None:
                continue

            available_rankings += 1

            st.metric(
                label=ranking_definition["label"],
                value=f"{ranking}ª su {valid_count}",
            )

        if available_rankings == 0:
            st.info(
                "Non sono disponibili ranking nazionali "
                "per questa provincia."
            )


# ==========================================================
# Profilo demografico
# ==========================================================

section_header(
    title="Struttura demografica",
    subtitle=(
        "Confronto tra la provincia selezionata e la media nazionale "
        "delle principali fasce di popolazione."
    ),
)

with st.container(border=True):

    demographic_columns = [
        {
            "label": "15-34 anni",
            "column": "perc_15_34",
        },
        {
            "label": "Over 65",
            "column": "perc_over65",
        },
    ]

    demographic_rows = []

    for demographic_indicator in demographic_columns:

        column = demographic_indicator["column"]

        provincial_value = safe_value(
            province_row,
            column,
        )

        national_value = province_df[column].mean()

        demographic_rows.extend(
            [
                {
                    "Indicatore": demographic_indicator["label"],
                    "Area": selected_province,
                    "Percentuale": provincial_value,
                },
                {
                    "Indicatore": demographic_indicator["label"],
                    "Area": "Media nazionale",
                    "Percentuale": national_value,
                },
            ]
        )

    demographic_df = pd.DataFrame(demographic_rows)

    demographic_figure = go.Figure()

    for area, color in [
        (selected_province, PRIMARY_BLUE),
        ("Media nazionale", LIGHT_BLUE),
    ]:

        area_df = demographic_df[
            demographic_df["Area"] == area
        ]

        demographic_figure.add_trace(
            go.Bar(
                name=area,
                x=area_df["Indicatore"],
                y=area_df["Percentuale"],
                marker_color=color,
                text=area_df["Percentuale"],
                texttemplate="%{text:.1f}%",
                textposition="outside",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"{area}: "
                    "%{y:.2f}%"
                    "<extra></extra>"
                ),
            )
        )

    demographic_figure.update_layout(
        barmode="group",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
    )

    demographic_figure = apply_standard_layout(
        demographic_figure,
        title="Provincia e media nazionale",
        height=410,
        show_legend=True,
    )

    demographic_figure.update_xaxes(
        title=None,
        showgrid=False,
    )

    demographic_figure.update_yaxes(
        title="Quota sulla popolazione (%)",
        gridcolor=LIGHT_GREY,
        zeroline=False,
    )

    st.plotly_chart(
        demographic_figure,
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )


# ==========================================================
# Club presenti
# ==========================================================

section_header(
    title="Club presenti nella provincia",
    subtitle=(
        "Società di Serie A e Serie B localizzate nel territorio "
        "selezionato."
    ),
)

with st.container(border=True):

    if not selected_clubs.empty:

        club_table = selected_clubs[
            [
                "club",
                "lega",
                "città",
                "brand_power_index",
                "numero_brand_sponsor",
            ]
        ].copy()

        club_table["Scheda club"] = club_table["club"].apply(
            lambda club_name: (
                f"./Scheda_club?club={quote(str(club_name))}"
            )
        )

        club_table = club_table.rename(
            columns={
                "club": "Club",
                "lega": "Campionato",
                "città": "Città",
                "brand_power_index": "Brand Power Index",
                "numero_brand_sponsor": "Numero sponsor",
            }
        )

        st.dataframe(
            club_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Club": st.column_config.TextColumn(
                    "Club",
                    width="large",
                ),
                "Campionato": st.column_config.TextColumn(
                    "Campionato",
                    width="small",
                ),
                "Città": st.column_config.TextColumn(
                    "Città",
                    width="medium",
                ),
                "Brand Power Index": st.column_config.NumberColumn(
                    "Brand Power Index",
                    format="%.3f",
                ),
                "Numero sponsor": st.column_config.NumberColumn(
                    "Numero sponsor",
                    format="%d",
                ),
                "Scheda club": st.column_config.LinkColumn(
                    "Approfondimento",
                    display_text="Apri scheda",
                ),
            },
        )

        st.caption(
            "I collegamenti alla Scheda Club saranno pienamente attivi "
            "dopo la creazione della pagina dedicata."
        )

    else:
        st.info(
            "La provincia selezionata non presenta club di Serie A "
            "o Serie B nel dataset."
        )


# ==========================================================
# Mappa provinciale
# ==========================================================

section_header(
    title="Localizzazione territoriale",
    subtitle=(
        "Il poligono evidenzia la provincia selezionata; i marker "
        "identificano i club presenti nel territorio."
    ),
)

with st.container(border=True):

    if selected_geo.empty:

        st.warning(
            "La geometria della provincia selezionata "
            "non è disponibile nel GeoJSON."
        )

    else:

        geometry_3857 = selected_geo.to_crs("EPSG:3857")
        centroid_3857 = geometry_3857.geometry.centroid.iloc[0]

        centroid_gdf = gpd.GeoSeries(
            [centroid_3857],
            crs="EPSG:3857",
        ).to_crs("EPSG:4326")

        map_center = {
            "lat": centroid_gdf.iloc[0].y,
            "lon": centroid_gdf.iloc[0].x,
        }

        map_zoom = calculate_map_zoom(selected_geo)

        geojson_data = selected_geo.__geo_interface__

        map_figure = go.Figure()

        map_figure.add_trace(
            go.Choroplethmapbox(
                geojson=geojson_data,
                locations=[selected_province],
                featureidkey="properties.provincia",
                z=[1],
                colorscale=[
                    [0, VERY_LIGHT_BLUE],
                    [1, SECONDARY_BLUE],
                ],
                showscale=False,
                marker={
                    "opacity": 0.50,
                    "line": {
                        "width": 2,
                        "color": PRIMARY_BLUE,
                    },
                },
                hovertemplate=(
                    f"<b>{selected_province}</b><br>"
                    f"Regione: {selected_region}<br>"
                    f"Club presenti: "
                    f"{format_integer(safe_value(province_row, 'numero_club'))}"
                    "<extra></extra>"
                ),
            )
        )

        clubs_with_coordinates = selected_clubs.dropna(
            subset=[
                "lat",
                "long",
            ]
        )

        if not clubs_with_coordinates.empty:

            map_figure.add_trace(
                go.Scattermapbox(
                    lat=clubs_with_coordinates["lat"],
                    lon=clubs_with_coordinates["long"],
                    mode="markers",
                    marker={
                        "size": 14,
                        "color": PRIMARY_BLUE,
                    },
                    text=clubs_with_coordinates["club"],
                    customdata=clubs_with_coordinates[
                        [
                            "lega",
                            "città",
                            "numero_brand_sponsor",
                            "brand_power_index",
                        ]
                    ],
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        "Campionato: %{customdata[0]}<br>"
                        "Città: %{customdata[1]}<br>"
                        "Numero sponsor: %{customdata[2]:.0f}<br>"
                        "Brand Power Index: %{customdata[3]:.3f}"
                        "<extra></extra>"
                    ),
                    name="Club",
                )
            )

        map_figure.update_layout(
            mapbox={
                "style": "open-street-map",
                "center": map_center,
                "zoom": map_zoom,
            },
            height=590,
            margin={
                "l": 0,
                "r": 0,
                "t": 0,
                "b": 0,
            },
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )

        st.plotly_chart(
            map_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )


# ==========================================================
# Esportazione
# ==========================================================

section_header(
    title="Dati della provincia",
    subtitle=(
        "Esporta gli indicatori utilizzati nella scheda territoriale."
    ),
)

export_columns = [
    "provincia",
    "regione",
    "numero_comuni",
    "numero_contribuenti",
    "reddito_complessivo_euro",
    "reddito_medio_provinciale_euro",
    "numero_club",
    "serie_a",
    "serie_b",
    "popolazione_residente",
    "pop_15_34",
    "perc_15_34",
    "pop_over65",
    "perc_over65",
    "eta_media",
    "club_per_100k",
    "numero_brand_sponsor",
    "brand_power_index",
]

available_export_columns = [
    column
    for column in export_columns
    if column in province_df.columns
]

export_df = province_rows[
    available_export_columns
].copy()

csv_data = export_df.to_csv(
    index=False,
).encode("utf-8-sig")

st.download_button(
    label=f"Scarica la scheda di {selected_province}",
    data=csv_data,
    file_name=(
        f"scheda_provincia_"
        f"{selected_province.lower().replace(' ', '_')}.csv"
    ),
    mime="text/csv",
    use_container_width=True,
)



with st.expander("Nota metodologica"):

    st.write(
        "Il radar rappresenta il percentile nazionale della provincia "
        "per ciascun indicatore disponibile. Un valore pari a 80 indica "
        "che la provincia presenta un risultato uguale o superiore "
        "a circa l’80% delle province considerate."
    )

    st.write(
        "Il Brand Power Index provinciale e il numero di brand sponsor "
        "sono disponibili esclusivamente per i territori nei quali "
        "il dataset registra club con informazioni commerciali associate."
    )

    st.write(
        "La mappa utilizza il GeoJSON provinciale in EPSG:4326 e "
        "sovrappone i punti dei club attraverso le coordinate presenti "
        "nel dataset delle società calcistiche."
    )

    