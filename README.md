# Social Brand Lab — Dashboard territoriale

Dashboard interattiva sviluppata per analizzare congiuntamente la distribuzione territoriale dei club calcistici italiani, la forza digitale dei brand sponsor e le caratteristiche economiche e demografiche delle province italiane.

Il progetto integra dati relativi ai club di Serie A e Serie B, indicatori social dei brand e informazioni territoriali, offrendo una lettura nazionale, provinciale e societaria del fenomeno.

## Dashboard online

La versione pubblica sarà disponibile al seguente indirizzo:

**[Apri la dashboard](INSERIRE_QUI_IL_LINK_STREAMLIT)**

Il collegamento verrà aggiornato dopo il deploy su Streamlit Community Cloud.

---

## Obiettivi

La dashboard è stata progettata per:

- analizzare la distribuzione geografica dei club di Serie A e Serie B;
- confrontare le province italiane attraverso indicatori calcistici, economici e demografici;
- misurare la forza digitale dei brand sponsor;
- approfondire il profilo delle singole province e dei singoli club;
- esplorare territorialmente i risultati mediante una mappa interattiva realizzata con Kepler.gl.

---

## Struttura della dashboard

### Home

Presentazione del progetto, del perimetro dell’analisi e dei principali dataset utilizzati.

### Panoramica nazionale

Sintesi nazionale della distribuzione dei club, dei territori coinvolti e degli indicatori commerciali associati.

### Analisi territoriale

Confronto tra le province italiane attraverso indicatori quali:

- numero di club;
- club ogni 100.000 abitanti;
- popolazione residente;
- reddito medio provinciale;
- quota di popolazione tra 15 e 34 anni;
- quota di popolazione over 65;
- età media;
- numero di brand sponsor;
- Brand Power Index.

### Brand e Sponsor

Analisi della forza digitale dei brand attraverso:

- Facebook;
- X;
- Instagram;
- YouTube;
- Brand Power Index;
- categorie economiche;
- presenza nei principali campionati europei.

### Scheda provincia

Approfondimento dedicato a ciascuna provincia, comprendente:

- indicatori demografici ed economici;
- numero e intensità dei club presenti;
- confronto con il quadro nazionale;
- ranking provinciale;
- elenco dei club localizzati nel territorio;
- rappresentazione cartografica.

### Scheda club

Profilo dei singoli club di Serie A e Serie B con:

- localizzazione geografica;
- campionato di appartenenza;
- numero di brand sponsor;
- Brand Power Index;
- ranking rispetto agli altri club;
- confronto con le società dello stesso campionato;
- collegamento alla provincia di appartenenza.

### Mappa interattiva

Visualizzazione Kepler.gl che integra:

- confini provinciali;
- indicatori territoriali;
- localizzazione dei club;
- informazioni demografiche, economiche e commerciali.

---

## Tecnologie utilizzate

- Python
- Streamlit
- Pandas
- GeoPandas
- Plotly
- Kepler.gl
- GeoJSON
- HTML
- GitHub
- Streamlit Community Cloud

---

## Struttura del repository

```text
.
├── .streamlit/
│   └── config.toml
├── dashboard/
│   ├── app.py
│   ├── assets/
│   │   └── logo_sbl.png
│   ├── pages/
│   │   ├── 1_Panoramica_nazionale.py
│   │   ├── 2_Analisi_territoriale.py
│   │   ├── 3_Brand_Sponsor.py
│   │   ├── 4_Scheda_provincia.py
│   │   ├── 5_Scheda_club.py
│   │   └── 6_Mappa_interattiva.py
│   ├── utils/
│   │   ├── components.py
│   │   ├── data.py
│   │   └── theme.py
│   └── requirements.txt
├── data/
│   └── processed/
├── outputs/
│   └── mappa_kepler_finale.html
├── .gitignore
└── README.md
```

Le cartelle contenenti notebook di sviluppo e dati grezzi non sono incluse nel repository pubblico, poiché non sono necessarie per l’esecuzione della dashboard.

---

## Esecuzione in locale

### 1. Clonare il repository

```bash
git clone INSERIRE_QUI_URL_REPOSITORY
cd INSERIRE_QUI_NOME_REPOSITORY
```

### 2. Creare un ambiente virtuale

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Su Windows:

```bash
.venv\Scripts\activate
```

### 3. Installare le dipendenze

```bash
pip install -r dashboard/requirements.txt
```

### 4. Avviare la dashboard

```bash
python3 -m streamlit run dashboard/app.py
```

La dashboard sarà disponibile, normalmente, all’indirizzo:

```text
http://localhost:8501
```

---

## Dataset

Il repository contiene esclusivamente i dataset elaborati necessari al funzionamento della dashboard.

I dati sono organizzati nella cartella:

```text
data/processed/
```

Tra i principali file utilizzati figurano:

- dataset dei club;
- dataset dei brand;
- indicatori provinciali;
- ranking e cluster dei brand;
- confini provinciali in formato GeoJSON;
- dati demografici ed economici provinciali.

I dati grezzi e i notebook utilizzati per la preparazione e la trasformazione delle fonti non sono inclusi nel repository pubblico.

---

## Metodologia

Il Brand Power Index sintetizza la forza digitale dei brand sulla base di indicatori normalizzati relativi alle principali piattaforme social.

La componente territoriale combina informazioni calcistiche, demografiche ed economiche su base provinciale. Le geometrie sono rappresentate nel sistema di riferimento EPSG:4326, compatibile con le applicazioni cartografiche web.

I ranking e i percentili visualizzati nella dashboard sono calcolati esclusivamente sui record per i quali l’indicatore considerato risulta disponibile.

---

## Autore

**Francesco Antonetti**

Progetto sviluppato nell’ambito del Social Brand Lab.

---

## Stato del progetto

Dashboard completata e predisposta per il deploy su Streamlit Community Cloud.