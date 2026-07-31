from urllib.parse import quote

import pandas as pd
import plotly.express as px
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



configure_page("Scheda club")

apply_theme()
render_sidebar()



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



club_df = load_club().copy()
province_df = load_province().copy()



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

province_text_columns = [
    "provincia",
    "regione",
]

province_numeric_columns = [
    "popolazione_residente",
    "reddito_medio_provinciale_euro",
    "numero_club",
    "club_per_100k",
    "numero_brand_sponsor",
    "brand_power_index",
]

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



def format_integer(value):
    """Formatta un numero intero secondo la convenzione italiana."""

    if pd.isna(value):
        return "N/D"

    return f"{int(round(value)):,}".replace(",", ".")


def format_decimal(value, decimals=3):
    """Formatta un numero decimale utilizzando la virgola."""

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
    """Formatta un importo in euro."""

    if pd.isna(value):
        return "N/D"

    return f"€ {format_integer(value)}"


def safe_value(row, column):
    """Restituisce il valore della colonna o NaN."""

    if column not in row.index:
        return float("nan")

    return row[column]


def national_rank(series, value, ascending=False):
    """Calcola il ranking del valore nella serie."""

    clean_series = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    if clean_series.empty or pd.isna(value):
        return None

    ranking = clean_series.rank(
        method="min",
        ascending=ascending,
    )

    matching_indices = clean_series[
        clean_series == value
    ].index

    if len(matching_indices) == 0:
        return None

    return int(ranking.loc[matching_indices].min())


def percentile_rank(series, value):
    """Calcola il percentile del valore nella serie."""

    clean_series = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    if clean_series.empty or pd.isna(value):
        return float("nan")

    return float((clean_series <= value).mean() * 100)


def get_query_club():
    """Legge il club eventualmente presente nell’URL."""

    query_value = st.query_params.get("club")

    if isinstance(query_value, list):
        query_value = query_value[0] if query_value else None

    if query_value is None:
        return None

    query_value = str(query_value).strip()

    available_clubs = (
        club_df["club"]
        .dropna()
        .astype(str)
        .tolist()
    )

    return next(
        (
            club_name
            for club_name in available_clubs
            if club_name.casefold() == query_value.casefold()
        ),
        None,
    )


def update_query_club(club_name):
    """Aggiorna il parametro club nell’URL."""

    current_value = st.query_params.get("club")

    if isinstance(current_value, list):
        current_value = current_value[0] if current_value else None

    if current_value != club_name:
        st.query_params["club"] = club_name


def apply_chart_layout(
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
            "l": 25,
            "r": 25,
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

    figure.update_xaxes(
        zeroline=False,
        linecolor=LIGHT_GREY,
        gridcolor=LIGHT_GREY,
    )

    figure.update_yaxes(
        zeroline=False,
        linecolor=LIGHT_GREY,
        gridcolor=LIGHT_GREY,
    )

    return figure



query_club = get_query_club()

if query_club is not None:
    query_league = club_df.loc[
        club_df["club"] == query_club,
        "lega",
    ].iloc[0]
else:
    query_league = None



page_header(
    eyebrow="Approfondimento societario",
    title="Scheda club",
    subtitle=(
        "Profilo interattivo dei club di Serie A e Serie B, con "
        "indicatori territoriali, commerciali e di Brand Power, "
        "confronto con gli altri club e localizzazione geografica."
    ),
)



with st.container(border=True):
    st.markdown("#### Seleziona il club")

    filter_col_1, filter_col_2 = st.columns(2)

    available_leagues = sorted(
        club_df["lega"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    default_league_index = 0

    if query_league in available_leagues:
        default_league_index = available_leagues.index(query_league)

    with filter_col_1:
        selected_league = st.selectbox(
            "Campionato",
            options=available_leagues,
            index=default_league_index,
        )

    available_clubs = sorted(
        club_df.loc[
            club_df["lega"] == selected_league,
            "club",
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    default_club_index = 0

    if (
        query_club in available_clubs
        and query_league == selected_league
    ):
        default_club_index = available_clubs.index(query_club)

    with filter_col_2:
        selected_club = st.selectbox(
            "Club",
            options=available_clubs,
            index=default_club_index,
        )


update_query_club(selected_club)


club_rows = club_df[
    club_df["club"] == selected_club
]

if club_rows.empty:
    st.error("Il club selezionato non è presente nel dataset.")
    st.stop()

club_row = club_rows.iloc[0]

selected_province = safe_value(club_row, "provincia")
selected_region = safe_value(club_row, "regione")

province_rows = province_df[
    province_df["provincia"] == selected_province
]

if not province_rows.empty:
    province_row = province_rows.iloc[0]
else:
    province_row = pd.Series(dtype="object")


with st.container(border=True):

    title_col, summary_col = st.columns([1.5, 1])

    with title_col:
        st.caption("CLUB SELEZIONATO")
        st.title(selected_club)
        st.write(
            f"{selected_league} — "
            f"{safe_value(club_row, 'città')}, "
            f"{selected_province}"
        )

    with summary_col:
        st.metric(
            label="Brand Power Index",
            value=format_decimal(
                safe_value(
                    club_row,
                    "brand_power_index",
                ),
                3,
            ),
        )

        st.caption(
            "Numero di brand sponsor: "
            f"{format_integer(safe_value(club_row, 'numero_brand_sponsor'))}"
        )


section_header(
    title="Profilo del club",
    subtitle=(
        "Informazioni societarie, territoriali e commerciali "
        "disponibili nel dataset."
    ),
)

kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

with kpi_col_1:
    kpi_card(
        label="Campionato",
        value=selected_league,
        subtitle="Categoria sportiva del club.",
    )

with kpi_col_2:
    kpi_card(
        label="Brand sponsor",
        value=format_integer(
            safe_value(
                club_row,
                "numero_brand_sponsor",
            )
        ),
        subtitle="Numero di brand associati nel dataset.",
    )

with kpi_col_3:
    kpi_card(
        label="Brand Power Index",
        value=format_decimal(
            safe_value(
                club_row,
                "brand_power_index",
            ),
            3,
        ),
        subtitle="Indicatore aggregato della forza digitale.",
    )

with kpi_col_4:
    kpi_card(
        label="Provincia",
        value=str(selected_province),
        subtitle=str(selected_region),
    )


section_header(
    title="Posizionamento competitivo",
    subtitle=(
        "Confronto del club selezionato rispetto agli altri club "
        "presenti nel dataset."
    ),
)

comparison_col_1, comparison_col_2 = st.columns([1.25, 0.75])


with comparison_col_1:
    with st.container(border=True):

        scatter_df = club_df[
            [
                "club",
                "lega",
                "numero_brand_sponsor",
                "brand_power_index",
                "regione",
            ]
        ].dropna(
            subset=[
                "numero_brand_sponsor",
                "brand_power_index",
            ]
        )

        if not scatter_df.empty:

            scatter_df["selezionato"] = scatter_df["club"].apply(
                lambda club_name: (
                    selected_club
                    if club_name == selected_club
                    else "Altri club"
                )
            )

            scatter_figure = px.scatter(
                scatter_df,
                x="numero_brand_sponsor",
                y="brand_power_index",
                color="selezionato",
                hover_name="club",
                custom_data=[
                    "lega",
                    "regione",
                ],
                color_discrete_map={
                    selected_club: PRIMARY_BLUE,
                    "Altri club": LIGHT_BLUE,
                },
            )

            scatter_figure.update_traces(
                marker={
                    "size": 12,
                    "opacity": 0.78,
                    "line": {
                        "width": 1,
                        "color": "white",
                    },
                },
                hovertemplate=(
                    "<b>%{hovertext}</b><br>"
                    "Campionato: %{customdata[0]}<br>"
                    "Regione: %{customdata[1]}<br>"
                    "Sponsor: %{x:.0f}<br>"
                    "Brand Power Index: %{y:.3f}"
                    "<extra></extra>"
                ),
            )

            selected_trace = scatter_figure.data[
                list(
                    scatter_figure.data[i].name
                    for i in range(len(scatter_figure.data))
                ).index(selected_club)
            ] if selected_club in [
                trace.name for trace in scatter_figure.data
            ] else None

            if selected_trace is not None:
                selected_trace.marker.size = 20
                selected_trace.marker.symbol = "diamond"

            scatter_figure = apply_chart_layout(
                scatter_figure,
                title="Brand Power e numero di sponsor",
                height=500,
                show_legend=True,
            )

            scatter_figure.update_layout(
                legend={
                    "title": {
                        "text": None,
                    },
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": 1.02,
                    "xanchor": "left",
                    "x": 0,
                }
            )

            scatter_figure.update_xaxes(
                title="Numero di brand sponsor",
                dtick=1,
            )

            scatter_figure.update_yaxes(
                title="Brand Power Index",
            )

            st.plotly_chart(
                scatter_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili dati sufficienti "
                "per il confronto tra i club."
            )



with comparison_col_2:
    with st.container(border=True):

        st.markdown("#### Ranking nazionale")

        brand_power_value = safe_value(
            club_row,
            "brand_power_index",
        )

        sponsor_value = safe_value(
            club_row,
            "numero_brand_sponsor",
        )

        brand_power_rank = national_rank(
            club_df["brand_power_index"],
            brand_power_value,
            ascending=False,
        )

        sponsor_rank = national_rank(
            club_df["numero_brand_sponsor"],
            sponsor_value,
            ascending=False,
        )

        league_df = club_df[
            club_df["lega"] == selected_league
        ]

        league_brand_rank = national_rank(
            league_df["brand_power_index"],
            brand_power_value,
            ascending=False,
        )

        if brand_power_rank is not None:
            st.metric(
                label="Brand Power complessivo",
                value=(
                    f"{brand_power_rank}° "
                    f"su {club_df['brand_power_index'].notna().sum()}"
                ),
            )
        else:
            st.metric(
                label="Brand Power complessivo",
                value="N/D",
            )

        if sponsor_rank is not None:
            st.metric(
                label="Numero di sponsor",
                value=(
                    f"{sponsor_rank}° "
                    f"su {club_df['numero_brand_sponsor'].notna().sum()}"
                ),
            )
        else:
            st.metric(
                label="Numero di sponsor",
                value="N/D",
            )

        if league_brand_rank is not None:
            st.metric(
                label=f"Brand Power in {selected_league}",
                value=(
                    f"{league_brand_rank}° "
                    f"su {league_df['brand_power_index'].notna().sum()}"
                ),
            )
        else:
            st.metric(
                label=f"Brand Power in {selected_league}",
                value="N/D",
            )



section_header(
    title="Profilo relativo del club",
    subtitle=(
        "Gli indicatori sono espressi come percentile rispetto "
        "all’insieme dei club analizzati."
    ),
)

with st.container(border=True):

    indicator_labels = [
        "Brand Power",
        "Numero sponsor",
    ]

    indicator_values = [
        percentile_rank(
            club_df["brand_power_index"],
            safe_value(
                club_row,
                "brand_power_index",
            ),
        ),
        percentile_rank(
            club_df["numero_brand_sponsor"],
            safe_value(
                club_row,
                "numero_brand_sponsor",
            ),
        ),
    ]

    profile_figure = go.Figure()

    profile_figure.add_trace(
        go.Bar(
            x=indicator_values,
            y=indicator_labels,
            orientation="h",
            marker_color=[
                PRIMARY_BLUE,
                SECONDARY_BLUE,
            ],
            text=indicator_values,
            texttemplate="%{text:.1f}° percentile",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Percentile: %{x:.1f}"
                "<extra></extra>"
            ),
        )
    )

    profile_figure.add_vline(
        x=50,
        line_dash="dash",
        line_color=LIGHT_BLUE,
        annotation_text="Mediana",
        annotation_position="top",
    )

    profile_figure = apply_chart_layout(
        profile_figure,
        title="Posizionamento rispetto agli altri club",
        height=360,
    )

    profile_figure.update_xaxes(
        title="Percentile",
        range=[0, 110],
    )

    profile_figure.update_yaxes(
        title=None,
        showgrid=False,
    )

    st.plotly_chart(
        profile_figure,
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )


section_header(
    title="Contesto territoriale",
    subtitle=(
        "Principali indicatori della provincia in cui è localizzato "
        "il club."
    ),
)

territory_col_1, territory_col_2, territory_col_3 = st.columns(3)

with territory_col_1:
    kpi_card(
        label="Popolazione provinciale",
        value=format_integer(
            safe_value(
                province_row,
                "popolazione_residente",
            )
        ),
        subtitle=str(selected_province),
    )

with territory_col_2:
    kpi_card(
        label="Reddito medio provinciale",
        value=format_currency(
            safe_value(
                province_row,
                "reddito_medio_provinciale_euro",
            )
        ),
        subtitle="Valore medio per contribuente.",
    )

with territory_col_3:
    kpi_card(
        label="Club ogni 100.000 abitanti",
        value=format_decimal(
            safe_value(
                province_row,
                "club_per_100k",
            ),
            3,
        ),
        subtitle="Intensità calcistica provinciale.",
    )


with st.container(border=True):

    province_link = (
        f"./Scheda_provincia?"
        f"provincia={quote(str(selected_province))}"
    )

    st.link_button(
        label=f"Apri la Scheda Provincia di {selected_province}",
        url=province_link,
        use_container_width=True,
    )



section_header(
    title="Localizzazione del club",
    subtitle=(
        "Posizione geografica del club e riferimento al territorio "
        "provinciale."
    ),
)

with st.container(border=True):

    club_latitude = safe_value(
        club_row,
        "lat",
    )

    club_longitude = safe_value(
        club_row,
        "long",
    )

    if pd.isna(club_latitude) or pd.isna(club_longitude):

        st.warning(
            "Le coordinate del club selezionato "
            "non sono disponibili."
        )

    else:

        map_figure = go.Figure()

        map_figure.add_trace(
            go.Scattermapbox(
                lat=[club_latitude],
                lon=[club_longitude],
                mode="markers",
                marker={
                    "size": 20,
                    "color": PRIMARY_BLUE,
                },
                text=[selected_club],
                customdata=[
                    [
                        selected_league,
                        safe_value(club_row, "città"),
                        selected_province,
                        selected_region,
                        safe_value(
                            club_row,
                            "numero_brand_sponsor",
                        ),
                        safe_value(
                            club_row,
                            "brand_power_index",
                        ),
                    ]
                ],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Campionato: %{customdata[0]}<br>"
                    "Città: %{customdata[1]}<br>"
                    "Provincia: %{customdata[2]}<br>"
                    "Regione: %{customdata[3]}<br>"
                    "Numero sponsor: %{customdata[4]:.0f}<br>"
                    "Brand Power Index: %{customdata[5]:.3f}"
                    "<extra></extra>"
                ),
            )
        )

        map_figure.update_layout(
            mapbox={
                "style": "open-street-map",
                "center": {
                    "lat": club_latitude,
                    "lon": club_longitude,
                },
                "zoom": 9,
            },
            height=500,
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



section_header(
    title="Confronto con i club dello stesso campionato",
    subtitle=(
        "Tabella ordinabile con gli indicatori commerciali "
        "dei club appartenenti alla stessa lega."
    ),
)

comparison_table = club_df[
    club_df["lega"] == selected_league
][
    [
        "club",
        "città",
        "provincia",
        "numero_brand_sponsor",
        "brand_power_index",
    ]
].copy()

comparison_table = comparison_table.sort_values(
    "brand_power_index",
    ascending=False,
)

comparison_table["Scheda club"] = comparison_table["club"].apply(
    lambda club_name: (
        f"./Scheda_club?club={quote(str(club_name))}"
    )
)

comparison_table = comparison_table.rename(
    columns={
        "club": "Club",
        "città": "Città",
        "provincia": "Provincia",
        "numero_brand_sponsor": "Numero sponsor",
        "brand_power_index": "Brand Power Index",
    }
)

with st.container(border=True):

    st.dataframe(
        comparison_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Club": st.column_config.TextColumn(
                "Club",
                width="large",
            ),
            "Città": st.column_config.TextColumn(
                "Città",
                width="medium",
            ),
            "Provincia": st.column_config.TextColumn(
                "Provincia",
                width="medium",
            ),
            "Numero sponsor": st.column_config.NumberColumn(
                "Numero sponsor",
                format="%d",
            ),
            "Brand Power Index": st.column_config.NumberColumn(
                "Brand Power Index",
                format="%.3f",
            ),
            "Scheda club": st.column_config.LinkColumn(
                "Approfondimento",
                display_text="Apri scheda",
            ),
        },
    )

    export_df = comparison_table.drop(
        columns=["Scheda club"],
        errors="ignore",
    )

    csv_data = export_df.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        label=f"Scarica il confronto {selected_league}",
        data=csv_data,
        file_name=(
            f"confronto_club_"
            f"{selected_league.lower().replace(' ', '_')}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )