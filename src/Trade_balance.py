#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

#%% Load the Excel files from the SSB folder in raw
#Trade data
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'ssb')
trade_filename = 'Imports and exports of food.xlsx'
trade_df = pd.read_excel(os.path.join(file_path, trade_filename), header=3)

# Flashfill the 'Type' column with values from 'Unnamed: 0'
trade_df['Type'] = trade_df['Unnamed: 0'].ffill()
trade_df.drop(columns='Unnamed: 0', inplace=True)

# Rename 'Unnamed: 1' to 'Food Category'
trade_df.rename(columns={'Unnamed: 1': 'Food Category'}, inplace=True)

# Drop rows with missing values
trade_df.dropna(inplace=True)

# Create a dictionary to map the food categories
category_mapping = {
    '00 Live animals other than animals of div.03': 'Meat',
    '01 Meat and meat preparations': 'Meat',
    "02 Dairy products and birds' eggs": 'Dairy and eggs',
    '03 Fish, crustaceans, molluscs and prep. thereof': 'Fish',
    '04 Cereals and cereal preparations': 'Grains and cereals',
    '05 Vegetables and fruit': 'Vegetables and Fruits',
    '06 Sugars, sugar preparations and honey': 'Sweets and snacks',
    '07 Coffee, tea, cocoa, spices': 'Miscellaneous',
    '09 Miscellaneous edible products': 'Miscellaneous',
    '11 Beverages': 'Beverages',
    '22 Oil seeds and oleaginous fruits': 'Fats and oils',
    '42 Fixed vegetable fats and oils, crude, refined or fractionated': 'Fats and oils',
    '43 Animal or vegetable fats and oils, processed': 'Fats and oils'
}

# Map the 'Food Category' values using the dictionary
trade_df['Food Category'] = trade_df['Food Category'].map(category_mapping)

# Drop rows with NA values after mapping
trade_df.dropna(inplace=True)

# Group by 'Food Category' and 'Type', summing the values for each year
trade_df_grouped = trade_df.groupby(['Food Category', 'Type'])[['2019', '2020', '2021', '2022', '2023']].sum().reset_index()

# Separate into Imports and Exports DataFrames
imports_df = trade_df_grouped[trade_df_grouped['Type'] == 'Imports'].set_index('Food Category')
exports_df = trade_df_grouped[trade_df_grouped['Type'] == 'Exports'].set_index('Food Category')

# Creating trade_df_avg where the average of the years is calculated
years = ['2019', '2020', '2021', '2022', '2023']
trade_df_avg = trade_df_grouped.copy()
trade_df_avg['Average'] = trade_df_avg[years].mean(axis=1)

# Separate into Imports and Exports DataFrames with average
imports_df_avg = trade_df_avg[trade_df_avg['Type'] == 'Imports'].set_index('Food Category')
exports_df_avg = trade_df_avg[trade_df_avg['Type'] == 'Exports'].set_index('Food Category')

#%%
#dict for colors
# Define the color scheme for food categories
food_group_colors = {
    'Fruits and nuts': '#186a3b',
    'Vegetables and Fruits': '#28b463',
    'Starchy vegetables': '#82e0aa',
    'Grains and cereals': '#abebc6',
    'Legumes': '#17a589',
    'Dairy and eggs': '#e59866',
    'Meat': '#d35400',
    'Fish': '#3498db',
    'Fats and oils': '#eaecee',
    'Sweets and snacks': '#808b96',
    'Beverages': '#aab7b8',
    'Miscellaneous': '#34495e'
}

#%%
# Plotting trade data
# Ensure food categories in both Imports and Exports are in the order of food_group_colors
categories_in_order = [cat for cat in food_group_colors.keys() if cat in imports_df.index]
# Plot the stacked bar plot for imports
fig, ax = plt.subplots(figsize=(10, 6))

imports_df.loc[categories_in_order, years].T.plot(
    kind='bar',
    stacked=True,
    color=[food_group_colors[cat] for cat in categories_in_order],
    ax=ax
)

# Customize the plot for Imports
ax.set_title('Imports by Food Category (2019-2023)')
ax.set_xlabel('Year')
ax.set_ylabel('Tons')
plt.xticks(rotation=0)
plt.tight_layout()

# Get the y-axis limits for imports
imports_ylim = ax.get_ylim()

# Show the plot for Imports
plt.show()

# Plot the stacked bar plot for exports
fig, ax = plt.subplots(figsize=(10, 6))

exports_df.loc[categories_in_order, years].T.plot(
    kind='bar',
    stacked=True,
    color=[food_group_colors[cat] for cat in categories_in_order],
    ax=ax
)

# Customize the plot for Exports
ax.set_title('Exports by Food Category (2019-2023)')
ax.set_xlabel('Year')
ax.set_ylabel('Tons')
plt.xticks(rotation=0)
plt.tight_layout()

# Set the y-axis limits for exports to match imports
ax.set_ylim(imports_ylim)

# Remove the legend
ax.get_legend().remove()

# Show the plot for Exports
plt.show()
