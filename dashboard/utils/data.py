import pandas as pd
import streamlit as st
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data" / "processed"


@st.cache_data
def load_province():

    return pd.read_csv(
        DATA / "province_master_finale.csv"
    )



@st.cache_data
def load_club():

    return pd.read_csv(
        DATA / "Squadre_serie_A_B_BPI.csv"
    )



@st.cache_data
def load_brand():

    return pd.read_csv(
        DATA / "brand_ranking.csv"
    )



@st.cache_data
def load_category():

    return pd.read_csv(
        DATA / "category_power.csv"
    )
    