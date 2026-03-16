# Boligmarked Analyse - Østfold

AI-drevet analyse av boligmarkedet i Østfold med web scraping, maskinlæring og interaktivt dashboard.

![Dashboard Preview](screenshots/dashboard.png)

## Prosjektbeskrivelse

Fullstack data science-prosjekt som:
- Scraper boligdata fra Finn.no
- Analyserer pristrender og mønstre
- Trener ML-modell for prisprediksjon
- Presenterer resultatene i interaktivt dashboard

**Resultater:**
- 1026 boliger analysert fra Østfold
- ML-modell med R² = 0.51
- Interaktivt dashboard med 4 analyse-tabs

## Teknologier

- **Data innhenting:** BeautifulSoup, requests
- **Databehandling:** Pandas, NumPy
- **Maskinlæring:** scikit-learn (Linear Regression)
- **Visualisering:** Plotly, Streamlit
- **Versjonskontroll:** Git, GitHub

## Installasjon

### Forutsetninger
- Python 3.11 eller 3.12
- pip

### Steg 1: Klon repository
```bash
git clone https://github.com/dittbrukernavn/boliganalyse.git
cd boliganalyse
```

### Steg 2: Installer avhengigheter
```bash
pip install -r requirements.txt
```

## Bruk

### 1. Hent boligdata
```bash
python scraper.py
```
Dette tar 5-10 minutter og lagrer data til `boliger_ostfold.csv`.

### 2. Kjør dashboard
```bash
streamlit run app.py
```
Åpner automatisk i nettleser på `localhost:8501`.

## Features

### 📊 Oversikt
- Prisfordeling (histogram)
- Prissprednng (box plot)
- Størrelse vs pris-analyse

### 🗺️ Per område
- Sammenligning mellom kommuner
- Pris per kvm-analyse
- Boligtype-fordeling

### 🤖 AI Priskalkulator
- ML-modell for prisprediksjon
- Input: størrelse, kommune, boligtype
- Sammenligning med lignende boliger

### 📈 Detaljert analyse
- Statistikk per kommune
- Rå data med filtrering

## Screenshots

![Priskalkulator](screenshots/kalkulator.png)
*AI-drevet priskalkulator med R² = 0.51*

![Analyse](screenshots/analyser.png)
*Statistikk og sammenligning per kommune*

## Utviklet av

Jørgen A. Fjellstad  
Bachelor i ingeniørfag - data, Høgskolen i Østfold  
[GitHub](https://github.com/Jorgenfje) | [LinkedIn](https://linkedin.com/in/jorgen-fjellstad)

## Lisens

MIT
