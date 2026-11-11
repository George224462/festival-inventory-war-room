import pandas as pd
import numpy as np
import os

# Set random seed for reproducibility
np.random.seed(42)

# Number of inventory items
num_items = 500

categories = {
    'Access & Security': ['RFID Wristbands', 'VIP Passes', 'Security Barriers', 'Lanyards', 'Metal Detectors'],
    'Beverage & Food': ['Beer Kegs (50L)', 'Bottled Water (24pk)', 'Energy Drink Cases', 'Ice Bags (20kg)', 'Eco Food Trays'],
    'Merchandise': ['Festival Hoodies', 'Artist T-Shirts', 'Posters (Limited)', 'Bucket Hats', 'Vinyl Stickers'],
    'Production & Stage': ['Stage Lights (LED)', 'PA Cables (50ft)', 'Generator Fuel (Liters)', 'Fog Machine Fluid', 'Pyrotechnic Flares'],
    'Camping & Comfort': ['2-Person Tents', 'Sleeping Bags', 'Portable Power Banks', 'Sanitizer Refills', 'Emergency Blankets']
}

items = []
category_list = []

for cat, item_names in categories.items():
    for _ in range(100):
        items.append(np.random.choice(item_names) + " #" + str(np.random.randint(100, 999)))
        category_list.append(cat)

# Generate realistic supply chain metrics
unit_cost = np.random.exponential(scale=35, size=num_items) + 1.5  # Cost per item ($1.50 to $300+)
annual_demand = np.random.negative_binomial(n=5, p=0.001, size=num_items) + 50 # High volume demand
lead_time_days = np.random.choice([3, 7, 14, 21, 30, 45], size=num_items) # Delivery time from supplier
demand_std_dev = annual_demand * np.random.uniform(0.05, 0.40, size=num_items) # Volatility in daily sales
current_stock = np.random.randint(0, annual_demand // 2, size=num_items)

# Introduce some missing data/dirty records to simulate realistic raw data
vendor_names = ['Global Access Supplies', 'Sound & Stage Co', 'BevCorp Logistics', 'Merch Direct Ltd', 'Event Shield Inc', np.nan]
vendors = np.random.choice(vendor_names, size=num_items)

df = pd.DataFrame({
    'item_id': [f"SKU-{1000 + i}" for i in range(num_items)],
    'item_name': items,
    'category': category_list,
    'unit_cost_usd': np.round(unit_cost, 2),
    'annual_demand_units': annual_demand,
    'demand_std_dev': np.round(demand_std_dev, 2),
    'lead_time_days': lead_time_days,
    'current_stock_units': current_stock,
    'vendor_name': vendors
})

# Ensure raw output directory exists
os.makedirs('data/raw', exist_ok=True)

# Save to CSV
output_path = 'data/raw/festival_inventory_raw.csv'
df.to_csv(output_path, index=False)
print(f"SUCCESS: Generated 500 inventory items saved to '{output_path}'")