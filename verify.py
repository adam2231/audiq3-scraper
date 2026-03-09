import pandas as pd
import requests
import time

def verify_stock_links():
    print("Loading your Audi Excel file...")
    try:
        df = pd.read_excel('audi_q3_stock.xlsx')
    except FileNotFoundError:
        print("Could not find audi_q3_stock.xlsx. Make sure it's in the same folder!")
        return
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    valid_cars = []
    print(f"Verifying {len(df)} cars to ensure they aren't hiding a sold-out redirect...\n")
    
    for index, row in df.iterrows():
        vin = row['VIN']
        url = row['URL']
        print(f"Checking {vin}...")
        
        try:
            # We use a full GET request this time to see the actual page code
            resp = requests.get(url, headers=headers, timeout=10)
            
            # 1. Check if the server redirected us normally
            if "soldout" in resp.url.lower():
                print("  ❌ Sold out (Server Redirect)")
                continue
                
            # 2. Check if the raw HTML contains the Javascript redirect trigger
            if "soldout" in resp.text.lower():
                print("  ❌ Sold out (JavaScript Redirect hiding in code)")
                continue
                
            print("  ✅ Verified In Stock!")
            valid_cars.append(row)
            
        except Exception as e:
            print(f"  ⚠️ Error checking {vin}: {e}")
            
        # Polite delay
        time.sleep(1)
        
    # Save the cleaned data
    clean_df = pd.DataFrame(valid_cars)
    clean_df.to_excel('audi_q3_stock_verified.xlsx', index=False)
    
    print(f"\nVerification complete! Removed {len(df) - len(clean_df)} sold-out cars.")
    print(f"Saved your {len(clean_df)} truly available cars to 'audi_q3_stock_verified.xlsx'.")

if __name__ == "__main__":
    verify_stock_links()