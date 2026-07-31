import pandas as pd
import plotly.express as px
import streamlit as st
from urllib.parse import quote

from utils.components import (
    kpi_card,
    page_header,
    render_sidebar,
    section_header,
)
from utils.data import load_province
from utils.theme import apply_theme, configure_page


configure_page("Analisi territoriale")

apply_theme()
render_sidebar()


PRIMARY_BLUE = "#173F56"
SECONDARY_BLUE = "#2C6E91"
LIGHT_BLUE = "#8FB9CE"
DARK_GREY = "#46545E"
LIGHT_GREY = "#E8EDF0"

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}


province_df = load_province().copy()


text_columns = [
    "provincia",
    "regione",
    "sigla_provincia",
    "club_presenti",
]

numeric_columns = [
    "numero_club",
    "serie_a",
    "serie_b",
    "popolazione_residente",
    "reddito_medio_provinciale_euro",
    "club_per_100k",
    "perc_15_34",
    "perc_over65",
    "eta_media",
    "numero_brand_sponsor",
    "brand_power_index",
]

for column in text_columns:
    if column in province_df.columns:
        province_df[column] = (
            province_df[column]
            .astype("string")
            .str.strip()
        )

for column in numeric_columns:
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
    """Formatta un importo in euro senza cifre decimali."""

    if pd.isna(value):
        return "N/D"

    return f"€ {format_integer(value)}"


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


def weighted_average(dataframe, value_column, weight_column):
    """Calcola una media ponderata ignorando i valori mancanti."""

    valid_data = dataframe[
        [value_column, weight_column]
    ].dropna()

    valid_data = valid_data[
        valid_data[weight_column] > 0
    ]

    if valid_data.empty:
        return float("nan")

    return (
        valid_data[value_column]
        .mul(valid_data[weight_column])
        .sum()
        / valid_data[weight_column].sum()
    )


page_header(
    eyebrow="Confronto provinciale",
    title="Analisi territoriale",
    subtitle=(
        "Confronto tra le province italiane attraverso indicatori "
        "calcistici, demografici ed economici, con particolare attenzione "
        "alla distribuzione dei club e alla loro rilevanza rispetto "
        "alla popolazione residente."
    ),
)



with st.container(border=True):
    st.markdown("#### Filtri territoriali")

    filter_col_1, filter_col_2 = st.columns(2)

    available_regions = sorted(
        province_df["regione"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with filter_col_1:
        selected_regions = st.multiselect(
            "Regione",
            options=available_regions,
            default=available_regions,
            placeholder="Seleziona una o più regioni",
        )

    province_options_df = province_df.copy()

    if selected_regions:
        province_options_df = province_options_df[
            province_options_df["regione"].isin(selected_regions)
        ]
    else:
        province_options_df = province_options_df.iloc[0:0]

    available_provinces = sorted(
        province_options_df["provincia"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with filter_col_2:
        selected_provinces = st.multiselect(
            "Provincia",
            options=available_provinces,
            default=[],
            placeholder="Tutte le province delle regioni selezionate",
        )


filtered_df = province_df.copy()

if selected_regions:
    filtered_df = filtered_df[
        filtered_df["regione"].isin(selected_regions)
    ]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_provinces:
    filtered_df = filtered_df[
        filtered_df["provincia"].isin(selected_provinces)
    ]


number_of_provinces = filtered_df["provincia"].nunique()
total_clubs = filtered_df["numero_club"].fillna(0).sum()
total_population = filtered_df["popolazione_residente"].fillna(0).sum()

average_income = weighted_average(
    filtered_df,
    "reddito_medio_provinciale_euro",
    "numero_contribuenti",
)

average_age = weighted_average(
    filtered_df,
    "eta_media",
    "popolazione_residente",
)


section_header(
    title="Indicatori territoriali",
    subtitle=(
        "Sintesi delle province incluse nei filtri selezionati."
    ),
)

kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

with kpi_col_1:
    kpi_card(
        label="Province selezionate",
        value=format_integer(number_of_provinces),
        subtitle="Unità territoriali incluse nell’analisi.",
    )

with kpi_col_2:
    kpi_card(
        label="Club presenti",
        value=format_integer(total_clubs),
        subtitle="Totale dei club localizzati nelle province selezionate.",
    )

with kpi_col_3:
    kpi_card(
        label="Popolazione residente",
        value=format_integer(total_population),
        subtitle="Somma della popolazione delle province selezionate.",
    )

with kpi_col_4:
    kpi_card(
        label="Reddito medio",
        value=format_currency(average_income),
        subtitle=(
            f"Età media ponderata: "
            f"{format_decimal(average_age, decimals=1)} anni."
        ),
    )



section_header(
    title="Posizionamento economico e calcistico",
    subtitle=(
        "Il grafico confronta il reddito medio provinciale con il numero "
        "di club ogni 100.000 abitanti. La dimensione delle bolle "
        "rappresenta la popolazione residente."
    ),
)

with st.container(border=True):

    scatter_df = filtered_df[
        [
            "provincia",
            "regione",
            "reddito_medio_provinciale_euro",
            "club_per_100k",
            "popolazione_residente",
            "numero_club",
            "eta_media",
        ]
    ].dropna(
        subset=[
            "reddito_medio_provinciale_euro",
            "club_per_100k",
            "popolazione_residente",
        ]
    )

    if not scatter_df.empty:

        scatter_figure = px.scatter(
            scatter_df,
            x="reddito_medio_provinciale_euro",
            y="club_per_100k",
            size="popolazione_residente",
            color="regione",
            hover_name="provincia",
            custom_data=[
                "regione",
                "numero_club",
                "popolazione_residente",
                "eta_media",
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
                "Regione: %{customdata[0]}<br>"
                "Reddito medio: € %{x:,.0f}<br>"
                "Club ogni 100.000 abitanti: %{y:.3f}<br>"
                "Numero di club: %{customdata[1]:.0f}<br>"
                "Popolazione: %{customdata[2]:,.0f}<br>"
                "Età media: %{customdata[3]:.1f} anni"
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
                    "text": "Regione",
                },
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "left",
                "x": 0,
            }
        )

        scatter_figure.update_xaxes(
            title="Reddito medio provinciale (€)",
            tickprefix="€ ",
            separatethousands=True,
        )

        scatter_figure.update_yaxes(
            title="Club ogni 100.000 abitanti",
        )

        st.plotly_chart(
            scatter_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

        st.caption(
            "Le province prive di club presentano un valore pari a zero "
            "sull’asse verticale. Le bolle più grandi identificano "
            "le province maggiormente popolose."
        )

    else:
        st.warning(
            "Non sono disponibili dati sufficienti per costruire "
            "il grafico con i filtri selezionati."
        )



section_header(
    title="Confronto tra regioni",
    subtitle=(
        "Distribuzione dei club e confronto della struttura demografica "
        "nelle regioni selezionate."
    ),
)

regional_col_1, regional_col_2 = st.columns(2)


with regional_col_1:
    with st.container(border=True):

        clubs_by_region = (
            filtered_df
            .groupby(
                "regione",
                as_index=False,
            )
            .agg(
                numero_club=("numero_club", "sum"),
                popolazione=("popolazione_residente", "sum"),
            )
            .sort_values(
                "numero_club",
                ascending=True,
            )
        )

        if not clubs_by_region.empty:

            clubs_region_figure = px.bar(
                clubs_by_region,
                x="numero_club",
                y="regione",
                orientation="h",
                text="numero_club",
                custom_data=["popolazione"],
            )

            clubs_region_figure.update_traces(
                marker_color=PRIMARY_BLUE,
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Club: %{x:.0f}<br>"
                    "Popolazione: %{customdata[0]:,.0f}"
                    "<extra></extra>"
                ),
            )

            clubs_region_figure = apply_chart_layout(
                clubs_region_figure,
                title="Numero di club per regione",
                height=500,
            )

            clubs_region_figure.update_xaxes(
                title="Numero di club",
                dtick=1,
            )

            clubs_region_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                clubs_region_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Nessuna regione disponibile per i filtri selezionati."
            )



with regional_col_2:
    with st.container(border=True):

        demographic_rows = []

        for region, region_df in filtered_df.groupby("regione"):

            young_average = weighted_average(
                region_df,
                "perc_15_34",
                "popolazione_residente",
            )

            elderly_average = weighted_average(
                region_df,
                "perc_over65",
                "popolazione_residente",
            )

            demographic_rows.append(
                {
                    "regione": region,
                    "15-34 anni": young_average,
                    "Over 65": elderly_average,
                }
            )

        demographic_df = pd.DataFrame(demographic_rows)

        if not demographic_df.empty:

            demographic_long_df = demographic_df.melt(
                id_vars="regione",
                value_vars=[
                    "15-34 anni",
                    "Over 65",
                ],
                var_name="fascia",
                value_name="percentuale",
            )

            demographic_figure = px.bar(
                demographic_long_df,
                x="percentuale",
                y="regione",
                color="fascia",
                orientation="h",
                barmode="group",
                text="percentuale",
                color_discrete_map={
                    "15-34 anni": SECONDARY_BLUE,
                    "Over 65": LIGHT_BLUE,
                },
            )

            demographic_figure.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "%{fullData.name}: %{x:.2f}%"
                    "<extra></extra>"
                ),
            )

            demographic_figure = apply_chart_layout(
                demographic_figure,
                title="Giovani e over 65 per regione",
                height=500,
                show_legend=True,
            )

            demographic_figure.update_layout(
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

            demographic_figure.update_xaxes(
                title="Quota sulla popolazione (%)",
            )

            demographic_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                demographic_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili dati demografici "
                "per i filtri selezionati."
            )


section_header(
    title="Ranking provinciali",
    subtitle=(
        "Province con la maggiore intensità calcistica e con il reddito "
        "medio più elevato nell’area selezionata."
    ),
)

ranking_col_1, ranking_col_2 = st.columns(2)


with ranking_col_1:
    with st.container(border=True):

        top_club_density = (
            filtered_df[
                [
                    "provincia",
                    "regione",
                    "club_per_100k",
                    "numero_club",
                ]
            ]
            .dropna(
                subset=[
                    "provincia",
                    "club_per_100k",
                ]
            )
            .query("club_per_100k > 0")
            .sort_values(
                "club_per_100k",
                ascending=False,
            )
            .head(15)
            .sort_values(
                "club_per_100k",
                ascending=True,
            )
        )

        if not top_club_density.empty:

            density_figure = px.bar(
                top_club_density,
                x="club_per_100k",
                y="provincia",
                orientation="h",
                text="club_per_100k",
                custom_data=[
                    "regione",
                    "numero_club",
                ],
            )

            density_figure.update_traces(
                marker_color=SECONDARY_BLUE,
                texttemplate="%{text:.3f}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Regione: %{customdata[0]}<br>"
                    "Club ogni 100.000 abitanti: %{x:.3f}<br>"
                    "Numero di club: %{customdata[1]:.0f}"
                    "<extra></extra>"
                ),
            )

            density_figure = apply_chart_layout(
                density_figure,
                title="Top 15 province per club ogni 100.000 abitanti",
                height=540,
            )

            density_figure.update_xaxes(
                title="Club ogni 100.000 abitanti",
            )

            density_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                density_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Nessuna provincia con club disponibile "
                "per i filtri selezionati."
            )


with ranking_col_2:
    with st.container(border=True):

        top_income = (
            filtered_df[
                [
                    "provincia",
                    "regione",
                    "reddito_medio_provinciale_euro",
                    "popolazione_residente",
                ]
            ]
            .dropna(
                subset=[
                    "provincia",
                    "reddito_medio_provinciale_euro",
                ]
            )
            .sort_values(
                "reddito_medio_provinciale_euro",
                ascending=False,
            )
            .head(15)
            .sort_values(
                "reddito_medio_provinciale_euro",
                ascending=True,
            )
        )

        if not top_income.empty:

            income_figure = px.bar(
                top_income,
                x="reddito_medio_provinciale_euro",
                y="provincia",
                orientation="h",
                text="reddito_medio_provinciale_euro",
                custom_data=[
                    "regione",
                    "popolazione_residente",
                ],
            )

            income_figure.update_traces(
                marker_color=PRIMARY_BLUE,
                texttemplate="€ %{text:,.0f}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Regione: %{customdata[0]}<br>"
                    "Reddito medio: € %{x:,.0f}<br>"
                    "Popolazione: %{customdata[1]:,.0f}"
                    "<extra></extra>"
                ),
            )

            income_figure = apply_chart_layout(
                income_figure,
                title="Top 15 province per reddito medio",
                height=540,
            )

            income_figure.update_xaxes(
                title="Reddito medio provinciale (€)",
                tickprefix="€ ",
                separatethousands=True,
            )

            income_figure.update_yaxes(
                title=None,
                showgrid=False,
            )

            st.plotly_chart(
                income_figure,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        else:
            st.info(
                "Non sono disponibili dati reddituali "
                "per i filtri selezionati."
            )




section_header(
    title="Dettaglio provinciale",
    subtitle=(
        "Tabella consultabile e ordinabile con i principali indicatori "
        "territoriali."
    ),
)

table_df = filtered_df[
    [
        "provincia",
        "regione",
        "numero_club",
        "club_per_100k",
        "popolazione_residente",
        "reddito_medio_provinciale_euro",
        "perc_15_34",
        "perc_over65",
        "eta_media",
    ]
].copy()

table_df = table_df.sort_values(
    [
        "numero_club",
        "provincia",
    ],
    ascending=[
        False,
        True,
    ],
)

table_df = table_df.rename(
    columns={
        "provincia": "Provincia",
        "regione": "Regione",
        "numero_club": "Numero club",
        "club_per_100k": "Club per 100.000",
        "popolazione_residente": "Popolazione",
        "reddito_medio_provinciale_euro": "Reddito medio",
        "perc_15_34": "15-34 anni (%)",
        "perc_over65": "Over 65 (%)",
        "eta_media": "Età media",
    }
)
table_df["Scheda provincia"] = table_df["Provincia"].apply(
    lambda province_name: (
        f"./Scheda_provincia?provincia={quote(str(province_name))}"
    )
)
with st.container(border=True):

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Provincia": st.column_config.TextColumn(
                "Provincia",
                width="medium",
            ),
            "Regione": st.column_config.TextColumn(
                "Regione",
                width="medium",
            ),
            "Numero club": st.column_config.NumberColumn(
                "Numero club",
                format="%d",
            ),
            "Club per 100.000": st.column_config.NumberColumn(
                "Club per 100.000",
                format="%.3f",
            ),
            "Popolazione": st.column_config.NumberColumn(
                "Popolazione",
                format="%d",
            ),
            "Reddito medio": st.column_config.NumberColumn(
                "Reddito medio",
                format="€ %.0f",
            ),
            "15-34 anni (%)": st.column_config.NumberColumn(
                "15-34 anni (%)",
                format="%.2f%%",
            ),
            "Over 65 (%)": st.column_config.NumberColumn(
                "Over 65 (%)",
                format="%.2f%%",
            ),
            "Età media": st.column_config.NumberColumn(
                "Età media",
                format="%.2f",
            ),
            "Scheda provincia": st.column_config.LinkColumn(
                "Approfondimento",
                 display_text="Apri scheda",
            ),
        },
    )

    csv_data = table_df.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        label="Scarica i dati territoriali visualizzati",
        data=csv_data,
        file_name="analisi_territoriale_province.csv",
        mime="text/csv",
        use_container_width=True,
    )


with st.expander("Nota metodologica"):

    st.write(
        "L’indicatore 'club ogni 100.000 abitanti' rapporta il numero "
        "di società calcistiche presenti nella provincia alla relativa "
        "popolazione residente. Consente quindi di confrontare territori "
        "di dimensioni demografiche differenti."
    )

    st.write(
        "Il reddito medio complessivo mostrato nei KPI è calcolato come "
        "media ponderata per il numero di contribuenti. Le percentuali "
        "demografiche e l’età media regionale sono ponderate per la "
        "popolazione residente delle province."
    )

    st.write(
        "Gli indicatori relativi ai brand sponsor non sono utilizzati "
        "come variabili principali in questa pagina perché sono disponibili "
        "solo per le province nelle quali è presente almeno un club "
        "con sponsor associati."
    )
    