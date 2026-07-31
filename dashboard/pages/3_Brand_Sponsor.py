from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.components import (
    kpi_card,
    page_header,
    render_sidebar,
    section_header,
)
from utils.data import load_brand
from utils.theme import apply_theme, configure_page


configure_page("Analisi dei brand sponsor")

apply_theme()
render_sidebar()



PRIMARY_BLUE = "#173F56"
SECONDARY_BLUE = "#2C6E91"
LIGHT_BLUE = "#8FB9CE"
DARK_GREY = "#46545E"
LIGHT_GREY = "#E8EDF0"

PLATFORM_COLORS = {
    "Facebook": "#173F56",
    "Instagram": "#2C6E91",
    "X": "#8FB9CE",
    "YouTube": "#5E7F91",
}

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}



brand_df = load_brand().copy()

project_root = Path(__file__).resolve().parents[2]

league_brand_path = (
    project_root
    / "data"
    / "processed"
    / "league_brand_clean.csv"
)

if league_brand_path.exists():
    league_brand_df = pd.read_csv(league_brand_path)
else:
    league_brand_df = pd.DataFrame()



text_columns = [
    "brand",
    "category",
]

numeric_columns = [
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

for column in text_columns:
    if column in brand_df.columns:
        brand_df[column] = (
            brand_df[column]
            .astype("string")
            .str.strip()
        )

for column in numeric_columns:
    if column in brand_df.columns:
        brand_df[column] = pd.to_numeric(
            brand_df[column],
            errors="coerce",
        )

if not league_brand_df.empty:

    for column in ["brand", "league"]:
        if column in league_brand_df.columns:
            league_brand_df[column] = (
                league_brand_df[column]
                .astype("string")
                .str.strip()
            )

brand_df["total_followers"] = (
    brand_df[
        [
            "facebook",
            "x",
            "instagram",
            "youtube",
        ]
    ]
    .fillna(0)
    .sum(axis=1)
)



def format_integer(value):
    """Formatta un numero intero secondo la convenzione italiana."""

    if pd.isna(value):
        return "N/D"

    return f"{int(round(value)):,}".replace(",", ".")


def format_decimal(value, decimals=3):
    """Formatta un numero decimale usando la virgola."""

    if pd.isna(value):
        return "N/D"

    formatted_value = f"{value:,.{decimals}f}"

    return (
        formatted_value
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )


def format_compact_number(value):
    """Formatta i follower in migliaia, milioni o miliardi."""

    if pd.isna(value):
        return "N/D"

    value = float(value)

    if value >= 1_000_000_000:
        return (
            f"{value / 1_000_000_000:.1f} mld"
            .replace(".", ",")
        )

    if value >= 1_000_000:
        return (
            f"{value / 1_000_000:.1f} mln"
            .replace(".", ",")
        )

    if value >= 1_000:
        return (
            f"{value / 1_000:.1f} mila"
            .replace(".", ",")
        )

    return format_integer(value)


def apply_chart_layout(
    figure,
    title=None,
    height=450,
    show_legend=False,
):
    """Applica uno stile uniforme ai grafici Plotly."""

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



page_header(
    eyebrow="Dimensione commerciale e digitale",
    title="Analisi dei brand sponsor",
    subtitle=(
        "Analisi della forza digitale dei brand inclusi nel Social "
        "Fanbase Tracking, con un approfondimento sulle categorie "
        "economiche, sulle piattaforme social e sulla presenza nei "
        "principali campionati europei."
    ),
)



with st.container(border=True):
    st.markdown("#### Filtri dell’analisi")

    if not league_brand_df.empty:
        filter_col_1, filter_col_2, filter_col_3 = st.columns(3)
    else:
        filter_col_1, filter_col_2 = st.columns(2)

    available_categories = sorted(
        brand_df["category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with filter_col_1:
        selected_categories = st.multiselect(
            "Categoria",
            options=available_categories,
            default=available_categories,
            placeholder="Seleziona una o più categorie",
        )

    category_filtered_df = brand_df.copy()

    if selected_categories:
        category_filtered_df = category_filtered_df[
            category_filtered_df["category"].isin(
                selected_categories
            )
        ]
    else:
        category_filtered_df = category_filtered_df.iloc[0:0]

    available_brands = sorted(
        category_filtered_df["brand"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with filter_col_2:
        selected_brands = st.multiselect(
            "Brand",
            options=available_brands,
            default=[],
            placeholder="Tutti i brand delle categorie selezionate",
        )

    selected_leagues = []

    if not league_brand_df.empty:

        available_leagues = sorted(
            league_brand_df["league"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        with filter_col_3:
            selected_leagues = st.multiselect(
                "Campionato",
                options=available_leagues,
                default=[],
                placeholder="Tutti i campionati disponibili",
            )



filtered_df = category_filtered_df.copy()

if selected_brands:
    filtered_df = filtered_df[
        filtered_df["brand"].isin(selected_brands)
    ]

if selected_leagues and not league_brand_df.empty:

    brands_in_selected_leagues = (
        league_brand_df[
            league_brand_df["league"].isin(selected_leagues)
        ]["brand"]
        .dropna()
        .unique()
        .tolist()
    )

    filtered_df = filtered_df[
        filtered_df["brand"].isin(brands_in_selected_leagues)
    ]


number_of_brands = filtered_df["brand"].nunique()
number_of_categories = filtered_df["category"].nunique()
average_brand_power = filtered_df["brand_power_index"].mean()
total_followers = filtered_df["total_followers"].sum()


section_header(
    title="Indicatori principali",
    subtitle=(
        "Sintesi del perimetro di brand selezionato e della relativa "
        "presenza digitale."
    ),
)

kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

with kpi_col_1:
    kpi_card(
        label="Brand selezionati",
        value=format_integer(number_of_brands),
        subtitle="Brand inclusi nei filtri correnti.",
    )

with kpi_col_2:
    kpi_card(
        label="Categorie rappresentate",
        value=format_integer(number_of_categories),
        subtitle="Settori economici presenti nella selezione.",
    )

with kpi_col_3:
    kpi_card(
        label="Brand Power medio",
        value=format_decimal(
            average_brand_power,
            decimals=3,
        ),
        subtitle="Media dell’indice dei brand selezionati.",
    )

with kpi_col_4:
    kpi_card(
        label="Follower complessivi",
        value=format_compact_number(total_followers),
        subtitle="Somma delle audience sulle quattro piattaforme.",
    )



section_header(
    title="Forza digitale dei brand",
    subtitle=(
        "Ranking dei brand sulla base del Brand Power Index e confronto "
        "della presenza complessiva sulle piattaforme social."
    ),
)

ranking_col_1, ranking_col_2 = st.columns(2)



with ranking_col_1:
    with st.container(border=True):

        top_brand_power = (
            filtered_df[
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
            .head(15)
            .sort_values(
                "brand_power_index",
                ascending=True,
            )
        )

        if not top_brand_power.empty:

            power_figure = px.bar(
                top_brand_power,
                x="brand_power_index",
                y="brand",
                orientation="h",
                text="brand_power_index",
                custom_data=["category"],
            )

            power_figure.update_traces(
                marker_color=PRIMARY_BLUE,
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

            power_figure = apply_chart_layout(
                power_figure,
                title="Top 15 brand per Brand Power Index",
                height=560,
            )

            power_figure.update_xaxes(
                title="Brand Power Index",
            )

            power_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                power_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Nessun brand disponibile per i filtri selezionati."
            )



with ranking_col_2:
    with st.container(border=True):

        top_followers = (
            filtered_df[
                [
                    "brand",
                    "category",
                    "total_followers",
                ]
            ]
            .dropna(
                subset=[
                    "brand",
                    "total_followers",
                ]
            )
            .sort_values(
                "total_followers",
                ascending=False,
            )
            .head(15)
            .sort_values(
                "total_followers",
                ascending=True,
            )
        )

        if not top_followers.empty:

            follower_figure = px.bar(
                top_followers,
                x="total_followers",
                y="brand",
                orientation="h",
                text="total_followers",
                custom_data=["category"],
            )

            follower_figure.update_traces(
                marker_color=SECONDARY_BLUE,
                texttemplate="%{text:.2s}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Categoria: %{customdata[0]}<br>"
                    "Follower complessivi: %{x:,.0f}"
                    "<extra></extra>"
                ),
            )

            follower_figure = apply_chart_layout(
                follower_figure,
                title="Top 15 brand per follower complessivi",
                height=560,
            )

            follower_figure.update_xaxes(
                title="Follower complessivi",
                separatethousands=True,
            )

            follower_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                follower_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili dati sui follower "
                "per i filtri selezionati."
            )


section_header(
    title="Distribuzione della fanbase",
    subtitle=(
        "Confronto tra Facebook, Instagram, X e YouTube per comprendere "
        "la composizione dell’audience digitale dei brand selezionati."
    ),
)

platform_col_1, platform_col_2 = st.columns(
    [0.8, 1.2]
)



with platform_col_1:
    with st.container(border=True):

        platform_totals = pd.DataFrame(
            {
                "Piattaforma": [
                    "Facebook",
                    "Instagram",
                    "X",
                    "YouTube",
                ],
                "Follower": [
                    filtered_df["facebook"].sum(),
                    filtered_df["instagram"].sum(),
                    filtered_df["x"].sum(),
                    filtered_df["youtube"].sum(),
                ],
            }
        )

        platform_figure = px.bar(
            platform_totals,
            x="Piattaforma",
            y="Follower",
            text="Follower",
            color="Piattaforma",
            color_discrete_map=PLATFORM_COLORS,
        )

        platform_figure.update_traces(
            texttemplate="%{text:.2s}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Follower: %{y:,.0f}"
                "<extra></extra>"
            ),
        )

        platform_figure = apply_chart_layout(
            platform_figure,
            title="Follower complessivi per piattaforma",
            height=470,
        )

        platform_figure.update_xaxes(
            title=None,
            showgrid=False,
        )

        platform_figure.update_yaxes(
            title="Follower",
            separatethousands=True,
        )

        st.plotly_chart(
            platform_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )



with platform_col_2:
    with st.container(border=True):

        platform_comparison = (
            filtered_df[
                [
                    "brand",
                    "facebook",
                    "instagram",
                    "x",
                    "youtube",
                    "total_followers",
                ]
            ]
            .dropna(subset=["brand"])
            .sort_values(
                "total_followers",
                ascending=False,
            )
            .head(10)
        )

        platform_long_df = platform_comparison.melt(
            id_vars=[
                "brand",
                "total_followers",
            ],
            value_vars=[
                "facebook",
                "instagram",
                "x",
                "youtube",
            ],
            var_name="piattaforma",
            value_name="follower",
        )

        platform_long_df["piattaforma"] = (
            platform_long_df["piattaforma"]
            .replace(
                {
                    "facebook": "Facebook",
                    "instagram": "Instagram",
                    "x": "X",
                    "youtube": "YouTube",
                }
            )
        )

        platform_comparison_figure = px.bar(
            platform_long_df,
            x="brand",
            y="follower",
            color="piattaforma",
            barmode="stack",
            color_discrete_map=PLATFORM_COLORS,
        )

        platform_comparison_figure.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>"
                "%{fullData.name}: %{y:,.0f}"
                "<extra></extra>"
            )
        )

        platform_comparison_figure = apply_chart_layout(
            platform_comparison_figure,
            title="Composizione social dei 10 brand con più follower",
            height=470,
            show_legend=True,
        )

        platform_comparison_figure.update_layout(
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

        platform_comparison_figure.update_xaxes(
            title=None,
            tickangle=-35,
            showgrid=False,
        )

        platform_comparison_figure.update_yaxes(
            title="Follower",
            separatethousands=True,
        )

        st.plotly_chart(
            platform_comparison_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )



section_header(
    title="Analisi per categoria economica",
    subtitle=(
        "Confronto tra diffusione delle categorie e forza media "
        "dei brand che vi appartengono."
    ),
)

category_col_1, category_col_2 = st.columns(2)



with category_col_1:
    with st.container(border=True):

        brands_by_category = (
            filtered_df
            .dropna(
                subset=[
                    "brand",
                    "category",
                ]
            )
            .groupby(
                "category",
                as_index=False,
            )
            .agg(
                numero_brand=("brand", "nunique")
            )
            .sort_values(
                "numero_brand",
                ascending=False,
            )
            .head(15)
            .sort_values(
                "numero_brand",
                ascending=True,
            )
        )

        if not brands_by_category.empty:

            category_count_figure = px.bar(
                brands_by_category,
                x="numero_brand",
                y="category",
                orientation="h",
                text="numero_brand",
            )

            category_count_figure.update_traces(
                marker_color=PRIMARY_BLUE,
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Numero di brand: %{x}"
                    "<extra></extra>"
                ),
            )

            category_count_figure = apply_chart_layout(
                category_count_figure,
                title="Top 15 categorie per numero di brand",
                height=530,
            )

            category_count_figure.update_xaxes(
                title="Numero di brand",
                dtick=1,
            )

            category_count_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                category_count_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Nessuna categoria disponibile "
                "per i filtri selezionati."
            )



with category_col_2:
    with st.container(border=True):

        category_power = (
            filtered_df
            .dropna(
                subset=[
                    "category",
                    "brand_power_index",
                ]
            )
            .groupby(
                "category",
                as_index=False,
            )
            .agg(
                brand_power_medio=(
                    "brand_power_index",
                    "mean",
                ),
                numero_brand=(
                    "brand",
                    "nunique",
                ),
            )
            .sort_values(
                "brand_power_medio",
                ascending=False,
            )
            .head(15)
            .sort_values(
                "brand_power_medio",
                ascending=True,
            )
        )

        if not category_power.empty:

            category_power_figure = px.bar(
                category_power,
                x="brand_power_medio",
                y="category",
                orientation="h",
                text="brand_power_medio",
                custom_data=["numero_brand"],
            )

            category_power_figure.update_traces(
                marker_color=SECONDARY_BLUE,
                texttemplate="%{text:.3f}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Brand Power medio: %{x:.3f}<br>"
                    "Numero di brand: %{customdata[0]}"
                    "<extra></extra>"
                ),
            )

            category_power_figure = apply_chart_layout(
                category_power_figure,
                title="Top 15 categorie per Brand Power medio",
                height=530,
            )

            category_power_figure.update_xaxes(
                title="Brand Power Index medio",
            )

            category_power_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                category_power_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili valori di Brand Power "
                "per le categorie selezionate."
            )


section_header(
    title="Audience social e Brand Power",
    subtitle=(
        "Il grafico mette in relazione la dimensione della fanbase "
        "su Instagram con il Brand Power Index. La dimensione della "
        "bolla rappresenta l’audience complessiva del brand."
    ),
)

with st.container(border=True):

    scatter_df = filtered_df[
        [
            "brand",
            "category",
            "instagram",
            "brand_power_index",
            "total_followers",
            "facebook",
            "x",
            "youtube",
        ]
    ].dropna(
        subset=[
            "brand",
            "instagram",
            "brand_power_index",
        ]
    )

    if not scatter_df.empty:

        scatter_figure = px.scatter(
            scatter_df,
            x="instagram",
            y="brand_power_index",
            size="total_followers",
            color="category",
            hover_name="brand",
            custom_data=[
                "category",
                "facebook",
                "x",
                "youtube",
                "total_followers",
            ],
            size_max=55,
        )

        scatter_figure.update_traces(
            marker={
                "opacity": 0.78,
                "line": {
                    "width": 1,
                    "color": "white",
                },
            },
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Categoria: %{customdata[0]}<br>"
                "Instagram: %{x:,.0f}<br>"
                "Brand Power Index: %{y:.3f}<br>"
                "Facebook: %{customdata[1]:,.0f}<br>"
                "X: %{customdata[2]:,.0f}<br>"
                "YouTube: %{customdata[3]:,.0f}<br>"
                "Follower complessivi: %{customdata[4]:,.0f}"
                "<extra></extra>"
            ),
        )

        scatter_figure = apply_chart_layout(
            scatter_figure,
            height=590,
            show_legend=True,
        )

        scatter_figure.update_layout(
            legend={
                "title": {
                    "text": "Categoria",
                },
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "left",
                "x": 0,
            }
        )

        scatter_figure.update_xaxes(
            title="Follower Instagram",
            separatethousands=True,
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
        st.warning(
            "Non sono disponibili dati sufficienti per costruire "
            "il grafico con i filtri selezionati."
        )



if not league_brand_df.empty:

    section_header(
        title="Presenza nei campionati europei",
        subtitle=(
            "Numero di brand presenti nei diversi campionati inclusi "
            "nel dataset League Brand."
        ),
    )

    with st.container(border=True):

        league_analysis_df = league_brand_df.copy()

        if not filtered_df.empty:
            league_analysis_df = league_analysis_df[
                league_analysis_df["brand"].isin(
                    filtered_df["brand"].dropna().unique()
                )
            ]

        brands_by_league = (
            league_analysis_df
            .dropna(
                subset=[
                    "brand",
                    "league",
                ]
            )
            .groupby(
                "league",
                as_index=False,
            )
            .agg(
                numero_brand=("brand", "nunique")
            )
            .sort_values(
                "numero_brand",
                ascending=True,
            )
        )

        if not brands_by_league.empty:

            league_figure = px.bar(
                brands_by_league,
                x="numero_brand",
                y="league",
                orientation="h",
                text="numero_brand",
            )

            league_figure.update_traces(
                marker_color=LIGHT_BLUE,
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Brand presenti: %{x}"
                    "<extra></extra>"
                ),
            )

            league_figure = apply_chart_layout(
                league_figure,
                title="Numero di brand per campionato",
                height=520,
            )

            league_figure.update_xaxes(
                title="Numero di brand",
                dtick=1,
            )

            league_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                league_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Nessuna associazione tra brand e campionati "
                "disponibile per i filtri selezionati."
            )



section_header(
    title="Dettaglio dei brand",
    subtitle=(
        "Tabella consultabile e ordinabile con gli indicatori social "
        "e il Brand Power Index."
    ),
)

table_df = filtered_df[
    [
        "brand",
        "category",
        "facebook",
        "instagram",
        "x",
        "youtube",
        "total_followers",
        "brand_power_index",
    ]
].copy()

table_df = table_df.sort_values(
    "brand_power_index",
    ascending=False,
)

table_df = table_df.rename(
    columns={
        "brand": "Brand",
        "category": "Categoria",
        "facebook": "Facebook",
        "instagram": "Instagram",
        "x": "X",
        "youtube": "YouTube",
        "total_followers": "Follower complessivi",
        "brand_power_index": "Brand Power Index",
    }
)

with st.container(border=True):

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Brand": st.column_config.TextColumn(
                "Brand",
                width="medium",
            ),
            "Categoria": st.column_config.TextColumn(
                "Categoria",
                width="medium",
            ),
            "Facebook": st.column_config.NumberColumn(
                "Facebook",
                format="%d",
            ),
            "Instagram": st.column_config.NumberColumn(
                "Instagram",
                format="%d",
            ),
            "X": st.column_config.NumberColumn(
                "X",
                format="%d",
            ),
            "YouTube": st.column_config.NumberColumn(
                "YouTube",
                format="%d",
            ),
            "Follower complessivi": st.column_config.NumberColumn(
                "Follower complessivi",
                format="%d",
            ),
            "Brand Power Index": st.column_config.NumberColumn(
                "Brand Power Index",
                format="%.3f",
            ),
        },
    )

    csv_data = table_df.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        label="Scarica i dati dei brand visualizzati",
        data=csv_data,
        file_name="analisi_brand_sponsor.csv",
        mime="text/csv",
        use_container_width=True,
    )



with st.expander("Nota metodologica"):

    st.write(
        "Il Brand Power Index sintetizza la forza digitale dei brand "
        "attraverso i valori normalizzati relativi a Facebook, X, "
        "Instagram e YouTube."
    )

    st.write(
        "Il totale dei follower è ottenuto sommando le audience delle "
        "quattro piattaforme. Tale valore rappresenta una misura "
        "aggregata e può includere utenti presenti contemporaneamente "
        "su più social network."
    )

    st.write(
        "Il dataset League Brand identifica la presenza dei brand nei "
        "campionati europei, ma non contiene una relazione diretta tra "
        "ciascun brand e uno specifico club. Per questa ragione la pagina "
        "analizza i brand e i campionati senza attribuire sponsor non "
        "esplicitamente presenti nei dati alle singole società."
    )
    