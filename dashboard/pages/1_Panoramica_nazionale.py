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
from utils.data import (
    load_brand,
    load_category,
    load_club,
    load_province,
)
from utils.theme import apply_theme, configure_page



configure_page("Panoramica nazionale")

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
brand_df = load_brand().copy()
category_df = load_category().copy()
province_df = load_province().copy()


numeric_columns_club = [
    "brand_power_index",
    "numero_brand_sponsor",
    "lat",
    "long",
]

numeric_columns_brand = [
    "facebook",
    "x",
    "instagram",
    "youtube",
    "facebook_norm",
    "x_norm",
    "instagram_norm",
    "youtube_norm",
    "brand_power_index",
]

numeric_columns_province = [
    "numero_club",
    "serie_a",
    "serie_b",
    "popolazione_residente",
    "numero_brand_sponsor",
    "brand_power_index",
    "reddito_medio_provinciale_euro",
    "club_per_100k",
]

for column in numeric_columns_club:
    if column in club_df.columns:
        club_df[column] = pd.to_numeric(
            club_df[column],
            errors="coerce",
        )

for column in numeric_columns_brand:
    if column in brand_df.columns:
        brand_df[column] = pd.to_numeric(
            brand_df[column],
            errors="coerce",
        )

for column in numeric_columns_province:
    if column in province_df.columns:
        province_df[column] = pd.to_numeric(
            province_df[column],
            errors="coerce",
        )



def format_integer(value):
    """
    Formatta i numeri interi utilizzando il separatore italiano
    delle migliaia.
    """

    if pd.isna(value):
        return "N/D"

    return f"{int(value):,}".replace(",", ".")


def format_decimal(value, decimals=3):
    """
    Formatta un numero decimale utilizzando la virgola.
    """

    if pd.isna(value):
        return "N/D"

    formatted_value = f"{value:,.{decimals}f}"

    return (
        formatted_value
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )


def clean_text_column(dataframe, column):
    """
    Rimuove spazi iniziali e finali da una colonna testuale.
    """

    if column in dataframe.columns:
        dataframe[column] = (
            dataframe[column]
            .astype("string")
            .str.strip()
        )


def apply_chart_layout(
    figure,
    title=None,
    height=420,
    show_legend=False,
):
    """
    Applica uno stile uniforme ai grafici Plotly.
    """

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
            "l": 20,
            "r": 20,
            "t": 65 if title else 25,
            "b": 30,
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
        showgrid=False,
        zeroline=False,
        linecolor=LIGHT_GREY,
    )

    figure.update_yaxes(
        showgrid=True,
        gridcolor=LIGHT_GREY,
        zeroline=False,
    )

    return figure


for dataframe, columns in [
    (
        club_df,
        [
            "club",
            "lega",
            "città",
            "provincia",
            "regione",
        ],
    ),
    (
        brand_df,
        [
            "brand",
            "category",
        ],
    ),
    (
        province_df,
        [
            "provincia",
            "regione",
            "club_presenti",
        ],
    ),
]:
    for column in columns:
        clean_text_column(dataframe, column)



with st.container(border=True):
    st.markdown("#### Filtri della panoramica")

    filter_col_1, filter_col_2 = st.columns(2)

    available_leagues = sorted(
        club_df["lega"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    available_regions = sorted(
        club_df["regione"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with filter_col_1:
        selected_leagues = st.multiselect(
            "Campionato",
            options=available_leagues,
            default=available_leagues,
            placeholder="Seleziona uno o più campionati",
        )

    with filter_col_2:
        selected_regions = st.multiselect(
            "Regione",
            options=available_regions,
            default=available_regions,
            placeholder="Seleziona una o più regioni",
        )


filtered_club_df = club_df.copy()

if selected_leagues:
    filtered_club_df = filtered_club_df[
        filtered_club_df["lega"].isin(selected_leagues)
    ]
else:
    filtered_club_df = filtered_club_df.iloc[0:0]

if selected_regions:
    filtered_club_df = filtered_club_df[
        filtered_club_df["regione"].isin(selected_regions)
    ]
else:
    filtered_club_df = filtered_club_df.iloc[0:0]


filtered_provinces = (
    filtered_club_df["provincia"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

filtered_province_df = province_df[
    province_df["provincia"].isin(filtered_provinces)
].copy()



page_header(
    eyebrow="Quadro generale",
    title="Panoramica nazionale",
    subtitle=(
        "Una vista sintetica della distribuzione dei club di Serie A "
        "e Serie B, della presenza territoriale e della forza digitale "
        "dei brand sponsor inclusi nell’analisi."
    ),
)



number_of_clubs = filtered_club_df["club"].dropna().nunique()
number_of_brands = brand_df["brand"].dropna().nunique()
number_of_categories = brand_df["category"].dropna().nunique()

average_brand_power = brand_df["brand_power_index"].mean()

number_of_active_regions = (
    filtered_club_df["regione"]
    .dropna()
    .nunique()
)


section_header(
    title="Indicatori principali",
    subtitle=(
        "Sintesi delle dimensioni considerate nella panoramica nazionale."
    ),
)

kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

with kpi_col_1:
    kpi_card(
        label="Club selezionati",
        value=format_integer(number_of_clubs),
        subtitle=(
            f"Distribuiti in {format_integer(number_of_active_regions)} "
            "regioni."
        ),
    )

with kpi_col_2:
    kpi_card(
        label="Brand analizzati",
        value=format_integer(number_of_brands),
        subtitle="Brand inclusi nel Social Fanbase Tracking.",
    )

with kpi_col_3:
    kpi_card(
        label="Categorie sponsor",
        value=format_integer(number_of_categories),
        subtitle="Settori merceologici rappresentati.",
    )

with kpi_col_4:
    kpi_card(
        label="Brand Power medio",
        value=format_decimal(
            average_brand_power,
            decimals=3,
        ),
        subtitle="Media dell’indice calcolato sui brand.",
    )



section_header(
    title="Distribuzione dei club",
    subtitle=(
        "Composizione per campionato e distribuzione territoriale "
        "delle società selezionate."
    ),
)

distribution_col_1, distribution_col_2 = st.columns(
    [0.85, 1.35]
)



with distribution_col_1:
    with st.container(border=True):

        league_distribution = (
            filtered_club_df
            .groupby("lega", dropna=False)["club"]
            .nunique()
            .reset_index(name="numero_club")
            .sort_values(
                "numero_club",
                ascending=False,
            )
        )

        if not league_distribution.empty:

            league_figure = go.Figure(
                data=[
                    go.Pie(
                        labels=league_distribution["lega"],
                        values=league_distribution["numero_club"],
                        hole=0.62,
                        textinfo="label+value",
                        textposition="outside",
                        marker={
                            "colors": [
                                PRIMARY_BLUE,
                                LIGHT_BLUE,
                            ]
                        },
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Club: %{value}<br>"
                            "Quota: %{percent}"
                            "<extra></extra>"
                        ),
                    )
                ]
            )

            league_figure.add_annotation(
                text=(
                    f"<b>{format_integer(number_of_clubs)}</b>"
                    "<br>club"
                ),
                x=0.5,
                y=0.5,
                showarrow=False,
                font={
                    "size": 17,
                    "color": PRIMARY_BLUE,
                },
            )

            league_figure = apply_chart_layout(
                league_figure,
                title="Club per campionato",
                height=430,
                show_legend=False,
            )

            st.plotly_chart(
                league_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.warning(
                "Nessun club disponibile per i filtri selezionati."
            )



with distribution_col_2:
    with st.container(border=True):

        clubs_by_region = (
            filtered_club_df
            .groupby("regione")["club"]
            .nunique()
            .reset_index(name="numero_club")
            .sort_values(
                "numero_club",
                ascending=True,
            )
        )

        if not clubs_by_region.empty:

            region_figure = px.bar(
                clubs_by_region,
                x="numero_club",
                y="regione",
                orientation="h",
                text="numero_club",
            )

            region_figure.update_traces(
                marker_color=SECONDARY_BLUE,
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Club: %{x}"
                    "<extra></extra>"
                ),
            )

            region_figure = apply_chart_layout(
                region_figure,
                title="Numero di club per regione",
                height=430,
            )

            region_figure.update_xaxes(
                title="Numero di club",
                dtick=1,
            )

            region_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                region_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.warning(
                "Nessuna regione disponibile per i filtri selezionati."
            )


section_header(
    title="Struttura del sistema sponsor",
    subtitle=(
        "Distribuzione dei brand tra le categorie economiche "
        "e ranking basato sul Brand Power Index."
    ),
)

sponsor_col_1, sponsor_col_2 = st.columns(2)



with sponsor_col_1:
    with st.container(border=True):

        brands_by_category = (
            brand_df
            .dropna(
                subset=[
                    "brand",
                    "category",
                ]
            )
            .groupby("category")["brand"]
            .nunique()
            .reset_index(name="numero_brand")
            .sort_values(
                "numero_brand",
                ascending=False,
            )
            .head(10)
            .sort_values(
                "numero_brand",
                ascending=True,
            )
        )

        category_figure = px.bar(
            brands_by_category,
            x="numero_brand",
            y="category",
            orientation="h",
            text="numero_brand",
        )

        category_figure.update_traces(
            marker_color=PRIMARY_BLUE,
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Brand: %{x}"
                "<extra></extra>"
            ),
        )

        category_figure = apply_chart_layout(
            category_figure,
            title="Top 10 categorie per numero di brand",
            height=470,
        )

        category_figure.update_xaxes(
            title="Numero di brand",
            dtick=1,
        )

        category_figure.update_yaxes(
            title=None,
            showgrid=False,
        )

        st.plotly_chart(
            category_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )



with sponsor_col_2:
    with st.container(border=True):

        top_brands = (
            brand_df[
                [
                    "brand",
                    "category",
                    "brand_power_index",
                ]
            ]
            .dropna(
                subset=[
                    "brand",
                    "brand_power_index",
                ]
            )
            .sort_values(
                "brand_power_index",
                ascending=False,
            )
            .head(10)
            .sort_values(
                "brand_power_index",
                ascending=True,
            )
        )

        brand_figure = px.bar(
            top_brands,
            x="brand_power_index",
            y="brand",
            orientation="h",
            text="brand_power_index",
            custom_data=["category"],
        )

        brand_figure.update_traces(
            marker_color=SECONDARY_BLUE,
            texttemplate="%{text:.3f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Categoria: %{customdata[0]}<br>"
                "Brand Power Index: %{x:.3f}"
                "<extra></extra>"
            ),
        )

        brand_figure = apply_chart_layout(
            brand_figure,
            title="Top 10 brand per Brand Power Index",
            height=470,
        )

        brand_figure.update_xaxes(
            title="Brand Power Index",
        )

        brand_figure.update_yaxes(
            title=None,
            showgrid=False,
        )

        st.plotly_chart(
            brand_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )



section_header(
    title="Concentrazione territoriale",
    subtitle=(
        "Province maggiormente interessate dalla presenza dei club "
        "e dei relativi brand sponsor."
    ),
)

territory_col_1, territory_col_2 = st.columns(2)



with territory_col_1:
    with st.container(border=True):

        provinces_by_clubs = (
            filtered_province_df[
                [
                    "provincia",
                    "regione",
                    "numero_club",
                ]
            ]
            .dropna(
                subset=[
                    "provincia",
                    "numero_club",
                ]
            )
            .query("numero_club > 0")
            .sort_values(
                "numero_club",
                ascending=False,
            )
            .head(10)
            .sort_values(
                "numero_club",
                ascending=True,
            )
        )

        if not provinces_by_clubs.empty:

            province_club_figure = px.bar(
                provinces_by_clubs,
                x="numero_club",
                y="provincia",
                orientation="h",
                text="numero_club",
                custom_data=["regione"],
            )

            province_club_figure.update_traces(
                marker_color=PRIMARY_BLUE,
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Regione: %{customdata[0]}<br>"
                    "Club: %{x}"
                    "<extra></extra>"
                ),
            )

            province_club_figure = apply_chart_layout(
                province_club_figure,
                title="Top 10 province per numero di club",
                height=460,
            )

            province_club_figure.update_xaxes(
                title="Numero di club",
                dtick=1,
            )

            province_club_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                province_club_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili dati provinciali "
                "per i filtri selezionati."
            )



with territory_col_2:
    with st.container(border=True):

        provinces_by_sponsors = (
            filtered_province_df[
                [
                    "provincia",
                    "regione",
                    "numero_brand_sponsor",
                ]
            ]
            .dropna(
                subset=[
                    "provincia",
                    "numero_brand_sponsor",
                ]
            )
            .query("numero_brand_sponsor > 0")
            .sort_values(
                "numero_brand_sponsor",
                ascending=False,
            )
            .head(10)
            .sort_values(
                "numero_brand_sponsor",
                ascending=True,
            )
        )

        if not provinces_by_sponsors.empty:

            province_sponsor_figure = px.bar(
                provinces_by_sponsors,
                x="numero_brand_sponsor",
                y="provincia",
                orientation="h",
                text="numero_brand_sponsor",
                custom_data=["regione"],
            )

            province_sponsor_figure.update_traces(
                marker_color=LIGHT_BLUE,
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Regione: %{customdata[0]}<br>"
                    "Brand sponsor: %{x}"
                    "<extra></extra>"
                ),
            )

            province_sponsor_figure = apply_chart_layout(
                province_sponsor_figure,
                title="Top 10 province per brand sponsor",
                height=460,
            )

            province_sponsor_figure.update_xaxes(
                title="Numero di brand sponsor",
                dtick=1,
            )

            province_sponsor_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                province_sponsor_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili dati sugli sponsor "
                "per le province selezionate."
            )


section_header(
    title="Dettaglio dei club",
    subtitle=(
        "Tabella consultabile e ordinabile con le principali "
        "informazioni relative ai club selezionati."
    ),
)

table_df = (
    filtered_club_df[
        [
            "club",
            "lega",
            "città",
            "provincia",
            "regione",
            "numero_brand_sponsor",
            "brand_power_index",
        ]
    ]
    .copy()
    .sort_values(
        [
            "lega",
            "club",
        ]
    )
)

table_df = table_df.rename(
    columns={
        "club": "Club",
        "lega": "Campionato",
        "città": "Città",
        "provincia": "Provincia",
        "regione": "Regione",
        "numero_brand_sponsor": "Numero sponsor",
        "brand_power_index": "Brand Power Index",
    }
)
from urllib.parse import quote

table_df["Scheda club"] = table_df["Club"].apply(
    lambda club_name:
        f"./Scheda_club?club={quote(str(club_name))}"
)
with st.container(border=True):

    st.dataframe(
        table_df,
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
            "Provincia": st.column_config.TextColumn(
                "Provincia",
                width="medium",
            ),
            "Regione": st.column_config.TextColumn(
                "Regione",
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

    csv_data = table_df.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        label="Scarica i dati visualizzati",
        data=csv_data,
        file_name="panoramica_nazionale_club.csv",
        mime="text/csv",
        use_container_width=True,
    )



with st.expander("Nota metodologica"):

    st.write(
        "Il Brand Power Index sintetizza la forza digitale dei brand "
        "sulla base degli indicatori normalizzati relativi a Facebook, "
        "X, Instagram e YouTube. I conteggi territoriali derivano "
        "dall’associazione tra club, province e regioni presente nei "
        "dataset integrati."
    )

    st.write(
        "I filtri relativi a campionato e regione si applicano ai club "
        "e alle analisi territoriali. I grafici dedicati alla struttura "
        "degli sponsor rappresentano invece l’intero insieme dei brand "
        "inclusi nel Social Fanbase Tracking."
    )
    