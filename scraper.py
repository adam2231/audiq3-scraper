import requests
import re
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_audi_inventory():
    # 1. Fetch the master list (Your validated URL)
    master_list_url = "https://gotowedoodbioru.audi.pl/ajax/get2.php?p=1&c=100&m%5B%5D=Audi%20Q3%20e-hybrid&s=price&d=asc&rm=2025"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    print("Fetching master list...")
    response = requests.get(master_list_url, headers=headers)
    items = response.json() if isinstance(response.json(), list) else response.json().get('items', [])
        
    print(f"Found {len(items)} cars. Starting deep scrape of carousel options...\n")
    available_cars = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context()
        page = context.new_page()

        for car in items:
            vin = car.get('vin')
            link = car.get('link', '')
            match = re.search(r'sc_detail\.([a-zA-Z0-9=]+)\.html', link)
            if not match: continue
                
            frontend_url = f"https://www.audi.pl/pl/wyszukiwarka-samochodow-nowych/details/:/id{match.group(1)}"
            print(f"Processing: {vin}")
            
            try:
                # Load the page
                page.goto(frontend_url, wait_until="domcontentloaded", timeout=30000)
                
                # Scroll down slightly to ensure the carousel loads into the DOM
                page.evaluate("window.scrollTo(0, 1000)")
                
                # Wait for the exact testid you found to appear in the code
                try:
                    page.wait_for_selector('p[data-testid="ProductItemText"]', timeout=8000)
                except:
                    pass # Some cars might not have additional packages

                # Grab only the text from elements with that specific data-testid
                package_elements = page.locator('p[data-testid="ProductItemText"]').all_inner_texts()
                
                # Clean up and remove duplicates
                cleaned_packages = list(set([p.strip() for p in package_elements if p.strip()]))
                packages_str = ", ".join(cleaned_packages) if cleaned_packages else "No additional packages"

                available_cars.append({
                    'VIN': vin,
                    'Model': car.get('model'),
                    'Price (PLN)': car.get('cena_vtp'),
                    'URL': frontend_url,
                    'Packages': packages_str
                })
                
            except Exception as e:
                print(f"  ⚠️ Could not scrape {vin}: {e}")

        browser.close()

    # Save to Excel
    df = pd.DataFrame(available_cars)
    df.to_excel('audi_q3_stock.xlsx', index=False)
    print(f"\nSuccess! Scraped {len(available_cars)} cars.")
    print("Run 'streamlit run app.py' to see the updated filters.")

if __name__ == "__main__":
    scrape_audi_inventory()