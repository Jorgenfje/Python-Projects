"""
Boligmarked Dashboard - Østfold
Interaktivt dashboard for boligprisanalyse
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np

# Page config
st.set_page_config(
    page_title="Boligmarked Østfold",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Last boligdata"""
    try:
        df = pd.read_csv('boliger_ostfold.csv')
        
        # DATA CLEANING - Fjern outliers
        # Realistiske grenser for boliger i Østfold:
        df = df[
            (df['storrelse_kvm'] >= 20) &      # Min 20 kvm (hybler)
            (df['storrelse_kvm'] <= 500) &     # Maks 500 kvm (store eneboliger)
            (df['pris'] >= 500000) &           # Min 500k (realistisk i Østfold)
            (df['pris'] <= 25000000) &         # Maks 25M (luksus)
            (df['pris_per_kvm'] >= 5000) &     # Min 5k/kvm
            (df['pris_per_kvm'] <= 150000)     # Maks 150k/kvm (leiligheter sentrum)
        ]
        
        return df
    except FileNotFoundError:
        st.error("⚠️ Fant ikke boliger_ostfold.csv - kjør scraper_final.py først!")
        st.stop()

def format_number(num):
    """Formater tall med norsk tallformat (mellomrom som tusenskiller)"""
    if pd.isna(num):
        return "N/A"
    return f"{int(num):,}".replace(",", " ")

def format_currency(num):
    """Formater som norske kroner"""
    if pd.isna(num):
        return "N/A"
    return f"{format_number(num)} kr"

@st.cache_data
def train_price_model(df):
    """Tren ML-modell for prisprediksjon med flere features"""
    # Fjern rader med manglende data
    df_model = df[['storrelse_kvm', 'kommune', 'boligtype', 'pris']].dropna()
    
    # Encode kategoriske variabler
    # One-hot encoding for kommune og boligtype
    df_encoded = pd.get_dummies(df_model, columns=['kommune', 'boligtype'], drop_first=True)
    
    # Separer features og target
    X = df_encoded.drop('pris', axis=1)
    y = df_encoded['pris']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Tren modell
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluer
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    # Returner også feature names for senere bruk
    feature_names = X.columns.tolist()
    
    return model, r2, mae, feature_names, df_encoded.columns.tolist()

def main():
    # Header
    st.markdown('<h1 class="main-header">🏠 Boligmarked Østfold</h1>', unsafe_allow_html=True)
    st.markdown("**AI-drevet analyse av boligpriser i Østfold**")
    st.markdown("---")
    
    # Last data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtrer data")
    
    # Kommune filter
    kommuner = ['Alle'] + sorted(df['kommune'].unique().tolist())
    valgt_kommune = st.sidebar.selectbox("Velg kommune:", kommuner)
    
    # Boligtype filter
    boligtyper = ['Alle'] + sorted(df['boligtype'].unique().tolist())
    valgt_type = st.sidebar.selectbox("Velg boligtype:", boligtyper)
    
    # Pris range
    min_pris = int(df['pris'].min())
    max_pris = int(df['pris'].max())
    pris_range = st.sidebar.slider(
        "Prisintervall (kr):",
        min_pris, max_pris,
        (min_pris, max_pris),
        step=100000,
        format="%d kr"
    )
    
    # Filtrer data
    df_filtered = df.copy()
    if valgt_kommune != 'Alle':
        df_filtered = df_filtered[df_filtered['kommune'] == valgt_kommune]
    if valgt_type != 'Alle':
        df_filtered = df_filtered[df_filtered['boligtype'] == valgt_type]
    df_filtered = df_filtered[
        (df_filtered['pris'] >= pris_range[0]) & 
        (df_filtered['pris'] <= pris_range[1])
    ]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Antall boliger", format_number(len(df_filtered)))
    with col2:
        st.metric("💰 Gjennomsnittspris", format_currency(df_filtered['pris'].mean()))
    with col3:
        st.metric("📏 Snitt størrelse", f"{df_filtered['storrelse_kvm'].mean():.0f} kvm")
    with col4:
        st.metric("📈 Pris/kvm", format_currency(df_filtered['pris_per_kvm'].mean()))
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Oversikt", "🗺️ Per område", "🤖 Priskalkulator", "📈 Analyser"])
    
    with tab1:
        st.header("Prisfordeling")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig_hist = px.histogram(
                df_filtered,
                x='pris',
                nbins=30,
                title='Prisfordeling',
                labels={'pris': 'Pris (kr)', 'count': 'Antall boliger'},
                color_discrete_sequence=['#667eea']
            )
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot
            fig_box = px.box(
                df_filtered,
                y='pris',
                title='Prissprednng (box plot)',
                labels={'pris': 'Pris (kr)'},
                color_discrete_sequence=['#764ba2']
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Scatter: Størrelse vs Pris
        st.subheader("Størrelse vs Pris")
        fig_scatter = px.scatter(
            df_filtered,
            x='storrelse_kvm',
            y='pris',
            color='boligtype',
            hover_data=['kommune', 'tittel'],
            title='Sammenheng mellom størrelse og pris',
            labels={'storrelse_kvm': 'Størrelse (kvm)', 'pris': 'Pris (kr)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab2:
        st.header("Sammenligning per område")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gjennomsnittspris per kommune
            avg_by_kommune = df.groupby('kommune')['pris'].mean().sort_values(ascending=True)
            fig_bar = px.bar(
                x=avg_by_kommune.values,
                y=avg_by_kommune.index,
                orientation='h',
                title='Gjennomsnittspris per kommune',
                labels={'x': 'Pris (kr)', 'y': 'Kommune'},
                color=avg_by_kommune.values,
                color_continuous_scale='blues'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pris per kvm per kommune
            avg_kvm_by_kommune = df.groupby('kommune')['pris_per_kvm'].mean().sort_values(ascending=True)
            fig_bar2 = px.bar(
                x=avg_kvm_by_kommune.values,
                y=avg_kvm_by_kommune.index,
                orientation='h',
                title='Pris per kvm per kommune',
                labels={'x': 'Kr/kvm', 'y': 'Kommune'},
                color=avg_kvm_by_kommune.values,
                color_continuous_scale='purples'
            )
            fig_bar2.update_layout(showlegend=False)
            st.plotly_chart(fig_bar2, use_container_width=True)
        
        # Antall boliger per boligtype
        st.subheader("Boligtyper")
        type_counts = df['boligtype'].value_counts()
        fig_pie = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title='Fordeling av boligtyper',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        st.header("🤖 AI Priskalkulator")
        st.markdown("Bruk maskinlæring til å predikere boligpris basert på størrelse, kommune og boligtype")
        
        # Tren modell
        model, r2, mae, feature_names, all_columns = train_price_model(df)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Inndata")
            
            # Input størrelse
            storrelse_input = st.slider(
                "Størrelse (kvm):",
                min_value=20,
                max_value=300,
                value=100,
                step=5
            )
            
            # Input kommune
            kommune_input = st.selectbox(
                "Velg kommune:",
                sorted(df['kommune'].unique())
            )
            
            # Input boligtype
            boligtype_input = st.selectbox(
                "Velg boligtype:",
                sorted(df['boligtype'].unique())
            )
            
            # Lag input array for modell
            # Opprett en rad med alle kolonner satt til 0
            input_data = pd.DataFrame(0, index=[0], columns=all_columns)
            
            # Sett størrelse
            input_data['storrelse_kvm'] = storrelse_input
            
            # Sett kommune (one-hot encoded)
            kommune_col = f'kommune_{kommune_input}'
            if kommune_col in input_data.columns:
                input_data[kommune_col] = 1
            
            # Sett boligtype (one-hot encoded)
            boligtype_col = f'boligtype_{boligtype_input}'
            if boligtype_col in input_data.columns:
                input_data[boligtype_col] = 1
            
            # Fjern pris-kolonnen (target)
            input_features = input_data.drop('pris', axis=1, errors='ignore')
            
            # Prediker
            predikert_pris = model.predict(input_features)[0]
            
            st.markdown("### Predikert pris:")
            st.markdown(f"## {format_currency(predikert_pris)}")
            
            st.info(f"""
            **Modell-nøyaktighet:**
            - R² score: {r2:.3f}
            - Gjennomsnittlig avvik: {format_currency(mae)}
            
            *Prediksjonen er basert på {format_number(len(df))} boliger i Østfold*
            
            **R² forklaring:**
            - 1.0 = Perfekt prediksjon
            - 0.7+ = God modell
            - 0.5-0.7 = OK modell
            - <0.5 = Svak modell
            """)
        
        with col2:
            st.subheader("Visualisering")
            
            # Sammenlign med faktiske boliger i samme kategori
            similar_boliger = df[
                (df['kommune'] == kommune_input) & 
                (df['boligtype'] == boligtype_input)
            ]
            
            if len(similar_boliger) > 0:
                fig_comparison = go.Figure()
                
                # Scatter av lignende boliger
                fig_comparison.add_trace(go.Scatter(
                    x=similar_boliger['storrelse_kvm'],
                    y=similar_boliger['pris'],
                    mode='markers',
                    name=f'{boligtype_input} i {kommune_input}',
                    marker=dict(size=8, color='lightblue', opacity=0.6)
                ))
                
                # Din prediksjon
                fig_comparison.add_trace(go.Scatter(
                    x=[storrelse_input],
                    y=[predikert_pris],
                    mode='markers',
                    name='Din prediksjon',
                    marker=dict(size=20, color='red', symbol='star')
                ))
                
                fig_comparison.update_layout(
                    title=f'Sammenligning: {boligtype_input} i {kommune_input}',
                    xaxis_title='Størrelse (kvm)',
                    yaxis_title='Pris (kr)',
                    hovermode='closest'
                )
                
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Statistikk for lignende boliger
                st.markdown("**Lignende boliger i markedet:**")
                st.write(f"- Antall: {len(similar_boliger)}")
                st.write(f"- Gjennomsnittspris: {format_currency(similar_boliger['pris'].mean())}")
                st.write(f"- Prisintervall: {format_currency(similar_boliger['pris'].min())} - {format_currency(similar_boliger['pris'].max())}")
            else:
                st.warning(f"Ingen {boligtype_input} funnet i {kommune_input} i datasettet.")
    
    with tab4:
        st.header("📈 Detaljert analyse")
        
        # Statistikk per kommune
        st.subheader("Statistikk per kommune")
        stats = df.groupby('kommune').agg({
            'pris': ['count', 'mean', 'median', 'min', 'max'],
            'storrelse_kvm': 'mean',
            'pris_per_kvm': 'mean'
        }).round(0)
        stats.columns = ['Antall', 'Snitt', 'Median', 'Min', 'Maks', 'Snitt kvm', 'Kr/kvm']
        stats = stats.sort_values('Antall', ascending=False)
        st.dataframe(stats, use_container_width=True)
        
        # Rå data
        st.subheader("Rå data (filtrert)")
        st.dataframe(
            df_filtered[['tittel', 'pris', 'storrelse_kvm', 'pris_per_kvm', 'boligtype', 'kommune']],
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Utviklet av Jørgen A. Fjellstad | Data hentet fra Finn.no | 
        <a href='https://github.com/Jorgenfje' target='_blank'>GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
