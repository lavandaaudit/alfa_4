import json
import pandas as pd
import re
import os

def sync():
    excel_path = 'catalog.xlsx'
    html_path = 'index.html'

    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return

    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return

    print("Reading catalog.xlsx...")
    # Load Products
    df_products = pd.read_excel(excel_path, sheet_name='Products')
    products = []
    for _, row in df_products.iterrows():
        # Parse colors
        colors = [c.strip() for c in str(row['colorTags']).split(',') if c.strip()]
        
        # Parse image from media JSON
        img = ""
        media_str = str(row['media'])
        try:
            media_json = json.loads(media_str)
            img = media_json.get('main', '')
        except Exception:
            # Fallback if it's not a JSON string, just use it raw
            img = media_str

        products.append({
            "id": str(row['id']),
            "name": str(row['name']),
            "cat": str(row['category']),
            "price": float(row['basePrice']),
            "colors": colors,
            "img": img,
            "lead": int(row['productionDays'])
        })

    # Load Kits
    df_kits = pd.read_excel(excel_path, sheet_name='Kits')
    kits = []
    for _, row in df_kits.iterrows():
        items_raw = []
        try:
            items_raw = json.loads(str(row['items']))
        except Exception as e:
            print(f"Warning: could not parse items for kit {row['id']}: {e}")
        
        items = []
        for item in items_raw:
            items.append({
                "id": item.get("productId"),
                "qty": item.get("defaultQty")
            })

        kits.append({
            "id": str(row['id']),
            "name": str(row['name']),
            "tagline": str(row['tagline']),
            "items": items
        })

    print(f"Parsed {len(products)} products and {len(kits)} kits.")

    # Format as pretty JS
    products_js = json.dumps(products, indent=4, ensure_ascii=False)
    kits_js = json.dumps(kits, indent=4, ensure_ascii=False)

    # Read index.html
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Regex to replace PRODUCTS and KITS arrays
    # We find the blocks starting from 'const PRODUCTS = [' to '];' and 'const KITS = [' to '];'
    print("Updating index.html content...")
    
    # Replace PRODUCTS
    pattern_products = r'(const PRODUCTS\s*=\s*\[)(.*?)(\];)'
    # Using a helper to replace safely without breaking other occurrences
    html_content = re.sub(
        r'const PRODUCTS\s*=\s*\[.*?\];', 
        f'const PRODUCTS = {products_js};', 
        html_content, 
        flags=re.DOTALL
    )

    # Replace KITS
    html_content = re.sub(
        r'const KITS\s*=\s*\[.*?\];', 
        f'const KITS = {kits_js};', 
        html_content, 
        flags=re.DOTALL
    )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Also update Next.js source JSON files if they exist
    next_products_path = 'src/data/products.json'
    next_kits_path = 'src/data/kits.json'

    if os.path.exists(next_products_path):
        # We need the original full product details from products.json or update the basic ones
        # For simplicity, let's write the parsed array into these files too
        print(f"Updating {next_products_path}...")
        # Since Excel might have other columns, let's read the full Excel rows to JSON
        excel_products_list = []
        for _, row in df_products.iterrows():
            item_dict = row.to_dict()
            # Restore JSON fields
            for k in ['tiers', 'media']:
                if k in item_dict and isinstance(item_dict[k], str):
                    try:
                        item_dict[k] = json.loads(item_dict[k])
                    except:
                        pass
            for k in ['colorTags', 'printOptions']:
                if k in item_dict and isinstance(item_dict[k], str):
                    item_dict[k] = [x.strip() for x in item_dict[k].split(',') if x.strip()]
            excel_products_list.append(item_dict)

        with open(next_products_path, 'w', encoding='utf-8') as f:
            json.dump(excel_products_list, f, indent=2, ensure_ascii=False)

    if os.path.exists(next_kits_path):
        print(f"Updating {next_kits_path}...")
        excel_kits_list = []
        for _, row in df_kits.iterrows():
            item_dict = row.to_dict()
            if 'items' in item_dict and isinstance(item_dict['items'], str):
                try:
                    item_dict['items'] = json.loads(item_dict['items'])
                except:
                    pass
            excel_kits_list.append(item_dict)

        with open(next_kits_path, 'w', encoding='utf-8') as f:
            json.dump(excel_kits_list, f, indent=2, ensure_ascii=False)

    print("Success! index.html and JSON files synced with catalog.xlsx")

if __name__ == '__main__':
    sync()
