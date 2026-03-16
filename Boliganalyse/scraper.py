"""
Boligmarked Analyse - Finn.no Scraper FINAL
Bruker korrekte Finn.no location IDs for Østfold
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict

class FinnScraper:
    def __init__(self):
        self.base_url = "https://www.finn.no"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_location(self, location_id: str, area_name: str, max_pages: int = 5) -> List[Dict]:
        """
        Scraper boliger for en spesifikk Finn.no location
        """
        boliger = []
        
        search_url = f"{self.base_url}/realestate/homes/search.html?location={location_id}"
        
        print(f"📍 {area_name}...", end=" ")
        
        for page in range(1, max_pages + 1):
            url = search_url if page == 1 else f"{search_url}&page={page}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                annonser = soup.find_all('article', class_='sf-search-ad')
                
                if not annonser:
                    break
                
                for annonse in annonser:
                    bolig_data = self._extract_bolig_data(annonse, area_name)
                    if bolig_data:
                        boliger.append(bolig_data)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Feil: {e}")
                break
        
        print(f"✓ {len(boliger)} boliger")
        return boliger
    
    def _extract_bolig_data(self, annonse, area_name: str) -> Dict:
        """Ekstraher data fra annonse"""
        try:
            # Finn lenke og Finn-kode
            lenke_tag = annonse.find('a', href=re.compile(r'/realestate/homes/ad.html'))
            lenke = None
            finn_kode = None
            
            if lenke_tag and lenke_tag.get('href'):
                lenke = self.base_url + lenke_tag['href']
                match = re.search(r'finnkode=(\d+)', lenke)
                if match:
                    finn_kode = match.group(1)
            
            # Finn pris
            pris = None
            pris_elements = annonse.find_all(string=re.compile(r'\d+.*kr', re.IGNORECASE))
            if pris_elements:
                pris = self._parse_pris(pris_elements[0])
            
            # Finn størrelse
            storrelse = None
            size_elements = annonse.find_all(string=re.compile(r'\d+\s*m²'))
            if size_elements:
                storrelse = self._parse_storrelse(size_elements[0])
            
            # Finn tittel
            tittel = None
            heading = annonse.find(['h2', 'h3'])
            if heading:
                tittel = heading.get_text(strip=True)
            
            # Finn boligtype
            text = annonse.get_text().lower()
            boligtype = 'Annet'
            if 'leilighet' in text:
                boligtype = 'Leilighet'
            elif 'enebolig' in text:
                boligtype = 'Enebolig'
            elif 'rekkehus' in text:
                boligtype = 'Rekkehus'
            elif 'tomannsbolig' in text:
                boligtype = 'Tomannsbolig'
            
            # Kun returner hvis vi har pris OG størrelse
            if pris and storrelse and pris > 100000 and storrelse > 10:  # Sanity check
                return {
                    'finn_kode': finn_kode,
                    'tittel': tittel,
                    'pris': pris,
                    'storrelse_kvm': storrelse,
                    'pris_per_kvm': round(pris / storrelse, 0),
                    'boligtype': boligtype,
                    'kommune': area_name,
                    'lenke': lenke
                }
            
            return None
            
        except:
            return None
    
    def _parse_pris(self, pris_text: str) -> float:
        """Parse pris"""
        if not pris_text:
            return None
        nummer = re.sub(r'[^\d]', '', pris_text)
        try:
            return float(nummer)
        except:
            return None
    
    def _parse_storrelse(self, size_text: str) -> float:
        """Parse størrelse"""
        if not size_text:
            return None
        match = re.search(r'(\d+)', size_text)
        if match:
            return float(match.group(1))
        return None


def scrape_ostfold_boliger():
    """
    Scrape boliger i Østfold med korrekte location IDs
    """
    scraper = FinnScraper()
    
    # Finn.no location IDs for Østfold
    locations = [
        ('1.20002.20022', 'Moss'),
        ('1.20002.20024', 'Fredrikstad'),
        ('1.20002.20021', 'Halden'),
        ('1.20002.22103', 'Indre Østfold'),
        ('1.20002.20023', 'Sarpsborg'),
        ('1.20002.20035', 'Råde'),
        ('1.20002.20034', 'Rakkestad'),
        ('1.20002.20025', 'Hvaler'),
        ('1.20002.20037', 'Våler'),
        ('1.20002.20033', 'Skiptvet'),
        ('2.20002.22103.23011', 'Askim'),
        ('2.20002.22103.23012', 'Eidsberg'),
        ('2.20002.22103.23013', 'Hobøl'),
        ('2.20002.22103.23010', 'Spydeberg'),
        ('2.20002.22103.23009', 'Trøgstad'),
    ]
    
    alle_boliger = []
    
    print("="*60)
    print("SCRAPER BOLIGMARKED - ØSTFOLD")
    print("="*60 + "\n")
    
    for location_id, area_name in locations:
        boliger = scraper.scrape_location(location_id, area_name, max_pages=5)
        alle_boliger.extend(boliger)
        time.sleep(2)
    
    if not alle_boliger:
        print("\n❌ Ingen boliger hentet!")
        return None
    
    # Lag DataFrame
    df = pd.DataFrame(alle_boliger)
    
    # Fjern duplikater
    df = df.drop_duplicates(subset=['finn_kode'], keep='first')
    
    print(f"\n{'='*60}")
    print(f"✅ Totalt {len(df)} unike boliger hentet")
    print(f"{'='*60}\n")
    
    # Lagre
    df.to_csv('boliger_ostfold.csv', index=False, encoding='utf-8')
    print(f"📁 Lagret til: boliger_ostfold.csv\n")
    
    # STATISTIKK
    print("="*60)
    print("STATISTIKK - ØSTFOLD BOLIGMARKED")
    print("="*60 + "\n")
    
    print(f"Gjennomsnittspris:       {df['pris'].mean():>12,.0f} kr")
    print(f"Median pris:             {df['pris'].median():>12,.0f} kr")
    print(f"Billigste:               {df['pris'].min():>12,.0f} kr")
    print(f"Dyreste:                 {df['pris'].max():>12,.0f} kr")
    print(f"\nGjennomsnittlig størrelse: {df['storrelse_kvm'].mean():>10.1f} kvm")
    print(f"Pris per kvm (snitt):      {df['pris_per_kvm'].mean():>10,.0f} kr\n")
    
    # Per kommune
    print("="*60)
    print("PER KOMMUNE")
    print("="*60 + "\n")
    
    per_kommune = df.groupby('kommune').agg({
        'pris': ['count', 'mean', 'median'],
        'pris_per_kvm': 'mean'
    }).round(0)
    per_kommune.columns = ['Antall', 'Snitt pris', 'Median', 'Kr/kvm']
    per_kommune = per_kommune.sort_values('Antall', ascending=False)
    print(per_kommune.to_string())
    
    # Per boligtype
    print("\n" + "="*60)
    print("PER BOLIGTYPE")
    print("="*60 + "\n")
    
    per_type = df.groupby('boligtype').agg({
        'pris': ['count', 'mean'],
        'pris_per_kvm': 'mean'
    }).round(0)
    per_type.columns = ['Antall', 'Snitt pris', 'Kr/kvm']
    per_type = per_type.sort_values('Antall', ascending=False)
    print(per_type.to_string())
    
    print("\n" + "="*60)
    print("✅ Data klar for analyse og visualisering!")
    print("="*60)
    
    return df


if __name__ == "__main__":
    df = scrape_ostfold_boliger()
