from __future__ import annotations

from typing import Optional

import streamlit as st

from utils.theme import (
    SBL_NAVY,
    SBL_NAVY_DARK,
    SBL_BLUE,
    SBL_BLUE_LIGHT,
    SBL_SKY,
    PAGE_BACKGROUND,
    CARD_BACKGROUND,
    SOFT_BACKGROUND,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    WHITE,
)



NAVIGATION_ITEMS = [
    {
        "path": "app.py",
        "label": "Home",
    },
    {
        "path": "pages/1_Panoramica_nazionale.py",
        "label": "Panoramica nazionale",
    },
    {
        "path": "pages/2_Analisi_territoriale.py",
        "label": "Analisi territoriale",
    },
    {
        "path": "pages/3_Brand_Sponsor.py",
        "label": "Brand e Sponsor",
    },
    {
        "path": "pages/4_Scheda_provincia.py",
        "label": "Scheda provincia",
    },
    {
        "path": "pages/5_Scheda_club.py",
        "label": "Scheda club",
    },
    {
        "path": "pages/6_Mappa_interattiva.py",
        "label": "Mappa interattiva",
    },
]


def render_sidebar() -> None:
    """
    Costruisce la sidebar personalizzata della dashboard.

    Il logo viene gestito da apply_theme() attraverso st.logo().
    Questa funzione si occupa esclusivamente dei testi informativi
    e dei collegamenti di navigazione.
    """

    with st.sidebar:

        st.markdown("### Dashboard territoriale")

        st.markdown(
            """
            **Club calcistici**  
            e brand sponsor
            """
        )

        st.divider()

        st.caption("Navigazione")

        for navigation_item in NAVIGATION_ITEMS:
            st.page_link(
                navigation_item["path"],
                label=navigation_item["label"],
                use_container_width=True,
            )

        st.divider()

        st.caption("Social Brand Lab")

        st.write(
            "Analisi territoriale della presenza dei club di Serie A "
            "e Serie B e della forza digitale dei brand sponsor."
        )


def page_header(
    eyebrow: str,
    title: str,
    subtitle: str,
) -> None:
    """
    Mostra l'intestazione principale della pagina.

    Utilizza esclusivamente componenti Streamlit nativi per garantire
    compatibilità e corretta visualizzazione del testo.
    """

    with st.container(border=True):

        st.caption(eyebrow.upper())

        st.title(title)

        if subtitle:
            st.write(subtitle)



def section_header(
    title: str,
    subtitle: Optional[str] = None,
) -> None:
    """
    Mostra il titolo e l'eventuale descrizione introduttiva
    di una sezione della dashboard.
    """

    st.subheader(title)

    if subtitle:
        st.caption(subtitle)



def kpi_card(
    label: str,
    value,
    subtitle: Optional[str] = None,
    delta=None,
    delta_color: str = "normal",
    accent: Optional[str] = None,
) -> None:
    """
    Mostra un indicatore sintetico.

    Il parametro accent viene mantenuto per compatibilità con le
    pagine già sviluppate. Lo stile cromatico generale è ora
    controllato centralmente da theme.py.
    """

    with st.container(border=True):

        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color,
        )

        if subtitle:
            st.caption(subtitle)


def content_card(
    title: str,
    text: Optional[str] = None,
    body: Optional[str] = None,
    subtitle: Optional[str] = None,
    accent: Optional[str] = None,
) -> None:
    """
    Mostra una card informativa.

    Sono accettati sia text sia body per garantire compatibilità
    con eventuali chiamate già presenti nelle pagine.
    """

    card_content = body if body is not None else text

    with st.container(border=True):

        st.markdown(f"#### {title}")

        if subtitle:
            st.caption(subtitle)

        if card_content:
            st.write(card_content)



def navigation_card(
    title: str,
    description: str,
    page: Optional[str] = None,
    page_path: Optional[str] = None,
    label: str = "Apri sezione",
    button_label: Optional[str] = None,
    accent: Optional[str] = None,
) -> None:
    """
    Mostra una card con collegamento verso un'altra pagina.

    Sono supportati sia page sia page_path per mantenere la
    compatibilità con il codice già presente nella Home.
    """

    destination = page_path if page_path is not None else page
    link_label = button_label if button_label is not None else label

    with st.container(border=True):

        st.markdown(f"#### {title}")

        st.write(description)

        if destination:
            st.page_link(
                destination,
                label=link_label,
                use_container_width=True,
            )



def vertical_space(lines: int = 1) -> None:
    """
    Inserisce spazio verticale tra le sezioni.

    Evita l'uso di HTML e mantiene il comportamento stabile
    nelle diverse versioni di Streamlit.
    """

    lines = max(0, int(lines))

    for _ in range(lines):
        st.write("")




def section_divider() -> None:
    """Inserisce un separatore orizzontale."""

    st.divider()



def information_box(
    title: str,
    message: str,
) -> None:
    """Mostra una nota informativa all'interno di una card."""

    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.write(message)

        