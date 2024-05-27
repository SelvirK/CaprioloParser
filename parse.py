import requests
from bs4 import BeautifulSoup
import json
import re
import chardet

def clean(tekst):
    # Zamenjuje tabove, nove redove i višestruke razmake jednim razmakom
    tekst = re.sub(r'[\t\n\r]+', ' ', tekst)
    tekst = re.sub(r'\s+', ' ', tekst)
    
    # Uklanja sve specijalne znakove osim slova, brojeva i osnovnih interpukcija
    tekst = re.sub(r'[^\w\s\.\,\!\?\-]', '', tekst)
    
    # Uklanja vodeće i prateće razmake
    tekst = tekst.strip()
    
    return tekst

base_url = 'https://jabihcapriolo.com/pretraga-det.php?pageNum_kat={pagenumber}&totalRows_kat=186'
result = []

for page_number in range(1):  # Idemo od 0 do 20 jer pageNum_kat kreće od 0
    print("Ucitavam page", page_number)
    url = base_url.format(pagenumber=page_number)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser',from_encoding="utf-8")
    
    artikli_divs = soup.find_all('div', class_='artikliLista artikliListaT artikliListaM artikliListaMM artikliListaMMM artikliListaL artikliListaXL artikliListaXXL')
    cnt=0
    for artikal in artikli_divs:
        
        cnt=cnt+1
        if cnt>3:
            break

        artikal_url = 'https://jabihcapriolo.com/' + artikal.find('a')['href']  # Pretpostavimo da je URL unutar <a> taga
        print("---------------------------------------------------------------------------------")
        print("Ucitavam stranu ", artikal_url)
        artikal_response = requests.get( artikal_url)
        artikal_soup = BeautifulSoup(artikal_response.content, 'html.parser',from_encoding="utf-16")
        
        naziv = clean(artikal_soup.find('div', class_='artikalNazvGlavni').text.strip())
        print(naziv)
        stara_cijena = artikal_soup.find('div', class_='cenaAkcDet')
        nova_cijena = clean(artikal_soup.find('div', class_='cenaDet').text.strip())

        if stara_cijena:
            stara_cijena=clean(stara_cijena.text.strip())
            print("stara_cijena", stara_cijena)
        


        print("nova_cijena", nova_cijena)
        
        specifikacije = {}
        bic_spec_divs = artikal_soup.find_all('div', class_='bicSpecRed')
        print(bic_spec_divs)
        for spec in bic_spec_divs:
            try:
                key = spec.find('div', class_='bicDetLeft')
                value = spec.find('div', class_='bicDetRight')

                if key and value:
                    key = str(key.text.strip())
                    value = str(value.text.strip())

                    print(key, value)
                    specifikacije[key] = value

                
            except Exception as e:      # works on python 3.x
                print('Exception: %s', repr(e))

            
        
        result.append({
            'Naziv': naziv,
            'StaraCijena': str(stara_cijena),
            'NovaCijena': str(nova_cijena),
            'Specifikacije': specifikacije,
            'URL': artikal_url
        })

# Snimanje rezultata u JSON fajl
with open('artikli.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
