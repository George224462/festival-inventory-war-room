import pandas as pd
import numpy as np
import sqlite3
import os

print("--- Starting Festival Inventory War Room Analytics Pipeline ---")

# 1. Load Raw Data
raw_path = 'data/raw/festival_inventory_raw.csv'
df = pd.read_csv(raw_path)

# 2. Data Cleaning
# Clean missing vendor names
df['vendor_name'] = df['vendor_name'].fillna('Unassigned Vendor')

# 3. Financial Metrics
df['annual_spend_usd'] = np.round(df['annual_demand_units'] * df['unit_cost_usd'], 2)

# 4. ABC Classification (Financial Value)
# Sort by spend descending
df = df.sort_values(by='annual_spend_usd', ascending=False).reset_index(drop=True)
df['cum_spend_usd'] = df['annual_spend_usd'].cumsum()
df['cum_spend_pct'] = df['cum_spend_usd'] / df['annual_spend_usd'].sum()

def get_abc_class(cum_pct):
    if cum_pct <= 0.80:
        return 'A'
    elif cum_pct <= 0.95:
        return 'B'
    else:
        return 'C'

df['abc_class'] = df['cum_pct'] = df['cum_spend_pct'].apply(get_abc_class)

# 5. XYZ Classification (Demand Predictability via Coefficient of Variation)
# CV = std_dev / mean
df['cv_demand'] = np.round(df['demand_std_dev'] / df['annual_demand_units'], 4)

def get_xyz_class(cv):
    if cv <= 0.15:
        return 'X'
    elif cv <= 0.25:
        return 'Y'
    else:
        return 'Z'

df['xyz_class'] = df['cv_demand'].apply(get_xyz_class)
df['abc_xyz_matrix'] = df['abc_class'] + df['xyz_class']

# 6. Safety Stock & Reorder Point (ROP) Calculation
# Service level Z = 1.645 for 95% availability
Z = 1.645
daily_demand = df['annual_demand_units'] / 365.0

# Safety Stock = Z * std_dev_demand * sqrt(lead_time_days / 30)
df['safety_stock_units'] = np.ceil(Z * df['demand_std_dev'] * np.sqrt(df['lead_time_days'] / 30.0)).astype(int)

# Reorder Point (ROP) = (Daily Demand * Lead Time) + Safety Stock
df['reorder_point_units'] = np.ceil((daily_demand * df['lead_time_days']) + df['safety_stock_units']).astype(int)

# Reorder Status Flag
df['reorder_flag'] = np.where(df['current_stock_units'] <= df['reorder_point_units'], 'CRITICAL: REORDER', 'OK')

# 7. Economic Order Quantity (EOQ)
# S = Fixed Ordering Cost ($50/order), H = Holding Cost (20% of unit cost per year)
S = 50.0
H = df['unit_cost_usd'] * 0.20
df['eoq_units'] = np.ceil(np.sqrt((2 * df['annual_demand_units'] * S) / H)).astype(int)

# Clean up final output column ordering
final_cols = [
    'item_id', 'item_name', 'category', 'vendor_name', 'unit_cost_usd',
    'annual_demand_units', 'annual_spend_usd', 'demand_std_dev', 'cv_demand',
    'lead_time_days', 'current_stock_units', 'safety_stock_units',
    'reorder_point_units', 'reorder_flag', 'eoq_units',
    'abc_class', 'xyz_class', 'abc_xyz_matrix'
]
df_clean = df[final_cols]

# 8. Export to Processed CSV and SQLite Database
os.makedirs('data/processed', exist_ok=True)
csv_out = 'data/processed/inventory_analytics_clean.csv'
df_clean.to_csv(csv_out, index=False)
print(f"SUCCESS: Saved processed dataset to '{csv_out}'")

db_out = 'data/festival_inventory.db'
conn = sqlite3.connect(db_out)
df_clean.to_sql('inventory_analytics', conn, if_exists='replace', index=False)
conn.close()
print(f"SUCCESS: Created SQLite database '{db_out}' with table 'inventory_analytics'")

# Summary Statistics
critical_count = len(df_clean[df_clean['reorder_flag'] == 'CRITICAL: REORDER'])
a_class_count = len(df_clean[df_clean['abc_class'] == 'A'])
print("\n--- Pipeline Summary ---")
print(f"Total SKUs Processed: {len(df_clean)}")
print(f"Class A (High Spend) Items: {a_class_count} ({a_class_count/len(df_clean)*100:.1f}%)")
print(f"Items Requiring Immediate Reorder: {critical_count}")