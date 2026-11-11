import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load clean data
df = pd.read_csv('data/processed/inventory_analytics_clean.csv')

# Build pivot table for count of SKUs across ABC and XYZ
pivot_count = df.pivot_table(index='xyz_class', columns='abc_class', values='item_id', aggfunc='count')

plt.figure(figsize=(8, 6))
sns.heatmap(pivot_count, annot=True, fmt="d", cmap="YlGnBu", cbar=True, linewidths=1)

plt.title('Festival Supply Chain: ABC-XYZ Inventory Matrix (SKU Count)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('ABC Classification (Financial Value / Spend)', fontsize=11, fontweight='bold')
plt.ylabel('XYZ Classification (Demand Volatility)', fontsize=11, fontweight='bold')

os.makedirs('images', exist_ok=True)
output_img = 'images/abc_xyz_matrix.png'
plt.tight_layout()
plt.savefig(output_img, dpi=300)
print(f"SUCCESS: Saved matrix visualization to '{output_img}'")