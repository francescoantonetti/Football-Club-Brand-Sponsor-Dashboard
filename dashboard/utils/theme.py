from pathlib import Path

import streamlit as st


DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = DASHBOARD_ROOT / "assets"


SBL_NAVY = "#173F56"
SBL_NAVY_DARK = "#102F41"
SBL_BLUE = "#255F7C"
SBL_BLUE_LIGHT = "#4F87A2"
SBL_SKY = "#A9C7D6"

PAGE_BACKGROUND = "#F3F7FA"
CARD_BACKGROUND = "#FFFFFF"
SOFT_BACKGROUND = "#EAF1F5"
INPUT_BACKGROUND = "#F8FAFC"

TEXT_PRIMARY = "#173F56"
TEXT_SECONDARY = "#526B79"
TEXT_MUTED = "#78909C"

BORDER_COLOR = "#D4E0E7"
BORDER_STRONG = "#B9CBD5"

WHITE = "#FFFFFF"
SUCCESS = "#2F7D67"
WARNING = "#B57A26"
ERROR = "#B94A48"

def find_sbl_logo() -> Path | None:
    """
    Individua automaticamente il logo SBL nella cartella assets.

    Vengono prima cercati alcuni nomi standard e successivamente
    qualsiasi immagine che contenga 'sbl' o 'logo' nel nome.
    """

    if not ASSETS_DIR.exists():
        return None

    supported_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".svg",
    }

    preferred_names = [
        "logo_sbl.png",
        "sbl_logo.png",
        "logo-sbl.png",
        "sbl-logo.png",
        "logo_sbl.svg",
        "sbl_logo.svg",
        "SBL.png",
        "sbl.png",
        "logo.png",
    ]

    for file_name in preferred_names:
        candidate = ASSETS_DIR / file_name

        if candidate.exists() and candidate.is_file():
            return candidate

    image_files = sorted(
        file_path
        for file_path in ASSETS_DIR.iterdir()
        if (
            file_path.is_file()
            and file_path.suffix.lower() in supported_extensions
        )
    )

    for image_file in image_files:
        if "sbl" in image_file.stem.lower():
            return image_file

    for image_file in image_files:
        if "logo" in image_file.stem.lower():
            return image_file

    if image_files:
        return image_files[0]

    return None


def configure_page(page_title: str) -> None:
    """
    Configura titolo, favicon, layout e sidebar.

    Questa funzione deve essere chiamata prima di qualsiasi altro
    comando Streamlit nella pagina.
    """

    logo_path = find_sbl_logo()

    page_icon = (
        str(logo_path)
        if logo_path is not None
        else ":material/analytics:"
    )

    st.set_page_config(
        page_title=f"{page_title} | SBL",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get help": None,
            "Report a bug": None,
            "About": (
                "Social Brand Lab — Dashboard territoriale dedicata "
                "all’analisi dei club calcistici e dei brand sponsor."
            ),
        },
    )


def render_sbl_logo() -> None:
    """
    Inserisce il logo ufficiale SBL nella parte superiore
    della sidebar.
    """

    logo_path = find_sbl_logo()

    if logo_path is not None:
        st.logo(
            str(logo_path),
            size="large",
        )


def apply_theme() -> None:
    """
    Applica il tema grafico globale della dashboard.

    Il tema interviene esclusivamente sull’aspetto visivo e non
    modifica la logica, i dati o la navigazione delle pagine.
    """

    render_sbl_logo()

    st.markdown(
        f"""
        <style>

        /* =====================================================
           VARIABILI GENERALI
        ===================================================== */

        :root {{
            --sbl-navy: {SBL_NAVY};
            --sbl-navy-dark: {SBL_NAVY_DARK};
            --sbl-blue: {SBL_BLUE};
            --sbl-blue-light: {SBL_BLUE_LIGHT};
            --sbl-sky: {SBL_SKY};

            --page-background: {PAGE_BACKGROUND};
            --card-background: {CARD_BACKGROUND};
            --soft-background: {SOFT_BACKGROUND};
            --input-background: {INPUT_BACKGROUND};

            --text-primary: {TEXT_PRIMARY};
            --text-secondary: {TEXT_SECONDARY};
            --text-muted: {TEXT_MUTED};

            --border-color: {BORDER_COLOR};
            --border-strong: {BORDER_STRONG};
        }}


        /* =====================================================
           APP E CONTENUTO PRINCIPALE
        ===================================================== */

        html,
        body,
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {{
            background-color: var(--page-background);
        }}

        html,
        body,
        p,
        div,
        span,
        label,
        input,
        textarea,
        select,
        button {{
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Helvetica,
                Arial,
                sans-serif;
        }}

        [data-testid="stMain"] {{
            background-color: var(--page-background);
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 1480px;
            padding-top: 2.75rem;
            padding-right: 3rem;
            padding-bottom: 4rem;
            padding-left: 3rem;
        }}

        .block-container {{
            max-width: 1480px;
            padding-top: 2.75rem;
            padding-right: 3rem;
            padding-bottom: 4rem;
            padding-left: 3rem;
        }}


        /* =====================================================
           TITOLI E TESTI
        ===================================================== */

        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {{
            color: var(--text-primary);
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            letter-spacing: -0.025em;
        }}

        h1 {{
            font-weight: 750;
            line-height: 1.12;
        }}

        h2 {{
            font-weight: 720;
            line-height: 1.18;
        }}

        h3,
        h4 {{
            font-weight: 680;
        }}

        p,
        [data-testid="stMarkdownContainer"] p {{
            color: var(--text-secondary);
            line-height: 1.65;
        }}

        [data-testid="stCaptionContainer"] {{
            color: var(--text-muted);
        }}

        [data-testid="stCaptionContainer"] p {{
            color: var(--text-muted);
            font-size: 0.88rem;
        }}


        /* =====================================================
           SIDEBAR
        ===================================================== */

        [data-testid="stSidebar"] {{
            min-width: 320px;
            width: 320px;
            background:
                linear-gradient(
                    180deg,
                    {SBL_NAVY_DARK} 0%,
                    {SBL_NAVY} 46%,
                    {SBL_BLUE} 100%
                );
            border-right: 1px solid rgba(255, 255, 255, 0.10);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            width: 320px;
        }}

        [data-testid="stSidebarContent"] {{
            padding-top: 1rem;
            padding-right: 1.25rem;
            padding-bottom: 2rem;
            padding-left: 1.25rem;
        }}
        [data-testid="stSidebarNav"] {{
        display: none !important;
        }}

        [data-testid="stSidebar"] * {{
            color: rgba(255, 255, 255, 0.94);
        }}

        [data-testid="stSidebar"] p {{
            color: rgba(255, 255, 255, 0.82);
        }}

        [data-testid="stSidebar"] hr {{
            border-color: rgba(255, 255, 255, 0.12);
            margin-top: 1.25rem;
            margin-bottom: 1.25rem;
        }}

        [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
            color: rgba(255, 255, 255, 0.62);
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }}


        /* =====================================================
           LOGO SBL
        ===================================================== */

        [data-testid="stLogo"] {{
            margin-top: 0.25rem;
            margin-bottom: 1.25rem;
            padding: 0.75rem 0.9rem;
            background-color: rgba(255, 255, 255, 0.97);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 14px;
        }}

        [data-testid="stLogo"] img {{
            display: block;
            width: auto;
            max-width: 230px;
            max-height: 72px;
            margin: 0 auto;
            object-fit: contain;
        }}


        /* =====================================================
           NAVIGAZIONE SIDEBAR
        ===================================================== */

        [data-testid="stSidebarNav"] {{
        display: none !important;
        }}


        [data-testid="stSidebarNavLink"],
        [data-testid="stPageLink-NavLink"] {{
            min-height: 42px;
            padding: 0.62rem 0.8rem;
            border: 1px solid transparent;
            border-radius: 9px;
            transition:
                background-color 140ms ease,
                border-color 140ms ease,
                transform 140ms ease;
        }}

        [data-testid="stSidebarNavLink"]:hover,
        [data-testid="stPageLink-NavLink"]:hover {{
            background-color: rgba(255, 255, 255, 0.10);
            border-color: rgba(255, 255, 255, 0.13);
            transform: translateX(2px);
        }}

        [data-testid="stSidebarNavLink"][aria-current="page"],
        [data-testid="stPageLink-NavLink"][aria-current="page"] {{
            background-color: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.23);
            box-shadow:
                inset 3px 0 0 rgba(255, 255, 255, 0.88);
        }}

        [data-testid="stSidebarNavLink"] span,
        [data-testid="stPageLink-NavLink"] span {{
            font-size: 0.93rem;
            font-weight: 540;
        }}

        [data-testid="stSidebarNavLink"][aria-current="page"] span,
        [data-testid="stPageLink-NavLink"][aria-current="page"] span {{
            color: {WHITE};
            font-weight: 680;
        }}


        /* =====================================================
           PULSANTE APERTURA SIDEBAR
        ===================================================== */

        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapsedControl"] button {{
            color: var(--sbl-navy);
            background-color: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }}


        /* =====================================================
           CONTAINER E CARD
        ===================================================== */

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            box-shadow:
                0 1px 2px rgba(16, 47, 65, 0.025),
                0 5px 16px rgba(16, 47, 65, 0.035);
            overflow: hidden;
        }}

        [data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: var(--border-strong);
        }}

        [data-testid="stVerticalBlockBorderWrapper"]
        > div:first-child {{
            padding: 1.05rem 1.1rem;
        }}


        /* =====================================================
           METRICHE E KPI
        ===================================================== */

        [data-testid="stMetric"] {{
            min-height: 126px;
            padding: 1rem 1.05rem;
            background:
                linear-gradient(
                    180deg,
                    {WHITE} 0%,
                    #F9FBFC 100%
                );
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--text-secondary);
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.01em;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--text-primary);
            font-size: 2rem;
            font-weight: 690;
            letter-spacing: -0.035em;
            line-height: 1.2;
        }}

        [data-testid="stMetricDelta"] {{
            color: var(--sbl-blue);
        }}


        /* =====================================================
           INPUT, SELECTBOX E MULTISELECT
        ===================================================== */

        [data-baseweb="select"] > div,
        [data-baseweb="base-input"],
        [data-testid="stTextInputRootElement"],
        [data-testid="stNumberInputContainer"] {{
            min-height: 44px;
            background-color: var(--input-background);
            border-color: var(--border-color);
            border-radius: 9px;
        }}

        [data-baseweb="select"] > div:hover,
        [data-baseweb="base-input"]:hover {{
            border-color: var(--sbl-blue-light);
        }}

        [data-baseweb="select"] > div:focus-within,
        [data-baseweb="base-input"]:focus-within {{
            border-color: var(--sbl-blue);
            box-shadow: 0 0 0 2px rgba(37, 95, 124, 0.12);
        }}

        [data-baseweb="tag"] {{
            color: {WHITE};
            background-color: var(--sbl-blue);
            border-radius: 6px;
        }}

        [data-baseweb="tag"] span {{
            color: {WHITE};
        }}

        [data-testid="stWidgetLabel"] p {{
            color: var(--text-primary);
            font-size: 0.88rem;
            font-weight: 570;
        }}


        /* =====================================================
           PULSANTI
        ===================================================== */

        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button,
        [data-testid="stLinkButton"] a {{
            min-height: 43px;
            padding: 0.6rem 1rem;
            color: {WHITE};
            background-color: var(--sbl-navy);
            border: 1px solid var(--sbl-navy);
            border-radius: 9px;
            font-weight: 620;
            transition:
                background-color 150ms ease,
                border-color 150ms ease,
                transform 150ms ease,
                box-shadow 150ms ease;
        }}

        [data-testid="stButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover,
        [data-testid="stLinkButton"] a:hover {{
            color: {WHITE};
            background-color: var(--sbl-blue);
            border-color: var(--sbl-blue);
            box-shadow: 0 4px 12px rgba(23, 63, 86, 0.15);
            transform: translateY(-1px);
        }}

        [data-testid="stButton"] button:active,
        [data-testid="stDownloadButton"] button:active,
        [data-testid="stLinkButton"] a:active {{
            transform: translateY(0);
            box-shadow: none;
        }}

        [data-testid="stButton"] button:focus-visible,
        [data-testid="stDownloadButton"] button:focus-visible,
        [data-testid="stLinkButton"] a:focus-visible {{
            outline: 3px solid rgba(79, 135, 162, 0.28);
            outline-offset: 2px;
        }}


        /* =====================================================
           DATAFRAME E TABELLE
        ===================================================== */

        [data-testid="stDataFrame"] {{
            overflow: hidden;
            border: 1px solid var(--border-color);
            border-radius: 10px;
        }}

        [data-testid="stDataFrame"] [role="columnheader"] {{
            color: var(--text-primary);
            background-color: var(--soft-background);
            font-weight: 650;
        }}

        [data-testid="stDataFrame"] [role="gridcell"] {{
            color: var(--text-secondary);
            border-color: #E7EEF2;
        }}


        /* =====================================================
           EXPANDER
        ===================================================== */

        [data-testid="stExpander"] {{
            background-color: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 11px;
            overflow: hidden;
        }}

        [data-testid="stExpander"] summary {{
            color: var(--text-primary);
            font-weight: 620;
        }}

        [data-testid="stExpander"] summary:hover {{
            background-color: var(--soft-background);
        }}


        /* =====================================================
           ALERT
        ===================================================== */

        [data-testid="stAlert"] {{
            border-radius: 10px;
            border-width: 1px;
        }}


        /* =====================================================
           GRAFICI PLOTLY
        ===================================================== */

        [data-testid="stPlotlyChart"] {{
            overflow: hidden;
            border-radius: 10px;
        }}


        /* =====================================================
           CODICE
        ===================================================== */

        code {{
            color: var(--sbl-navy);
            background-color: var(--soft-background);
            border-radius: 5px;
        }}

        [data-testid="stCodeBlock"] {{
            border: 1px solid var(--border-color);
            border-radius: 10px;
        }}


        /* =====================================================
           SCROLLBAR
        ===================================================== */

        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background-color: #B8C9D2;
            border: 2px solid transparent;
            border-radius: 999px;
            background-clip: padding-box;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background-color: #8FA9B7;
        }}


        /* =====================================================
           TOOLBAR E FOOTER STREAMLIT
        ===================================================== */

        [data-testid="stStatusWidget"] {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        #MainMenu {{
            visibility: hidden;
        }}


        /* =====================================================
           RESPONSIVE
        ===================================================== */

        @media (max-width: 1100px) {{

            [data-testid="stMainBlockContainer"],
            .block-container {{
                padding-top: 2rem;
                padding-right: 1.5rem;
                padding-left: 1.5rem;
            }}
        }}

        @media (max-width: 760px) {{

            [data-testid="stMainBlockContainer"],
            .block-container {{
                padding-top: 1.5rem;
                padding-right: 1rem;
                padding-left: 1rem;
            }}

            [data-testid="stMetricValue"] {{
                font-size: 1.65rem;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

    