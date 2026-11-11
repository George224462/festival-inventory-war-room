import pandas as pd
import os

print("--- Generating Excel Supply Chain Model ---")

# Load processed dataset
df = pd.read_csv('data/processed/inventory_analytics_clean.csv')

# Ensure output directory exists
os.makedirs('excel', exist_ok=True)
excel_path = 'excel/festival_inventory_model.xlsx'

# Create multi-tab Excel workbook
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    # Tab 1: All Inventory SKUs
    df.to_excel(writer, sheet_name='Inventory Master', index=False)
    
    # Tab 2: Critical Reorder War Room (Filtered to items needing reorder)
    reorder_df = df[df['reorder_flag'] == 'CRITICAL: REORDER'].sort_values(by='annual_spend_usd', ascending=False)
    reorder_df.to_excel(writer, sheet_name='Reorder War Room', index=False)
    
    # Tab 3: ABC-XYZ Matrix Aggregation
    matrix_df = df.groupby(['abc_class', 'xyz_class']).agg(
        total_skus=('item_id', 'count'),
        total_spend_usd=('annual_spend_usd', 'sum'),
        avg_lead_time=('lead_time_days', 'mean')
    ).reset_index()
    matrix_df.to_excel(writer, sheet_name='ABC-XYZ Matrix Summary', index=False)

print(f"SUCCESS: Exported Excel model with 3 tabs to '{excel_path}'")