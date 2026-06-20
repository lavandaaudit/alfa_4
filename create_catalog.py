import json
import pandas as pd
import os

with open('src/data/products.json', 'r') as f:
    products = json.load(f)

with open('src/data/kits.json', 'r') as f:
    kits = json.load(f)

# Flatten products
products_df = pd.DataFrame(products)
# Some fields are lists/dicts, convert to string so they can be written to Excel
products_df['tiers'] = products_df['tiers'].apply(lambda x: json.dumps(x))
products_df['media'] = products_df['media'].apply(lambda x: json.dumps(x))
products_df['colorTags'] = products_df['colorTags'].apply(lambda x: ','.join(x))
products_df['printOptions'] = products_df['printOptions'].apply(lambda x: ','.join(x))

# Flatten kits
kits_df = pd.DataFrame(kits)
kits_df['items'] = kits_df['items'].apply(lambda x: json.dumps(x))

# Create Excel writer
writer = pd.ExcelWriter('catalog.xlsx', engine='openpyxl')
products_df.to_excel(writer, sheet_name='Products', index=False)
kits_df.to_excel(writer, sheet_name='Kits', index=False)
writer.close()

print("catalog.xlsx created successfully")
