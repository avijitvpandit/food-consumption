#%%importing the libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os

#%%
# Load and clean the data
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'matvaretabell', 'all-foods.xlsx')
xls = pd.ExcelFile(file_path)

# Load the required sheets
foods_df = pd.read_excel(xls, sheet_name='Foods')
foods_nutrients_df = pd.read_excel(xls, sheet_name='Foods (all nutrients)')

# Forward fill the "Matvare ID" to populate category names
foods_nutrients_df['Matvare ID'] = foods_nutrients_df['Matvare ID'].fillna(method='ffill')

# Drop any rows that serve as category labels (i.e., where 'Matvare' is NaN)
foods_nutrients_cleaned = foods_nutrients_df.dropna(subset=['Matvare'])

# Select necessary columns from 'Foods'
foods_selected = foods_df[['Matvare', 'Kilokalorier (kcal)', 'Spiselig del (%)']]

# Select necessary columns from 'Foods (all nutrients)'
nutrients_selected = foods_nutrients_cleaned[['Matvare', 'Protein (g)', 'Fat (g)', 'Carbohydrate (g)', 'Water (g)', 
                                              'Phosphorus (P) (mg)', 'Sugar, total (g)']]

# Merge both datasets on 'Matvare'
combined_df = pd.merge(nutrients_selected, foods_selected, on='Matvare', how='inner')

# Define keyword-based mapping function to classify "Matvare" into the custom categories
def classify_food(item):
    item = str(item).lower()  # Convert to lowercase for easier matching
    
    # Mapping based on common terms
    if any(keyword in item for keyword in ['fruit', 'berry', 'nut']):
        return 'Fruits and nuts'
    elif 'vegetable' in item or 'lettuce' in item or 'broccoli' in item:
        return 'Vegetables'
    elif 'potato' in item:
        return 'Starchy vegetables'
    elif any(keyword in item for keyword in ['cereal', 'bread', 'grain', 'rice', 'pasta']):
        return 'Grains and cereals'
    elif any(keyword in item for keyword in ['milk', 'yoghurt', 'cream', 'cheese']):
        return 'Dairy and alternatives'
    elif any(keyword in item for keyword in ['beef', 'pork', 'lamb', 'meat', 'veal']):
        return 'Red meat'
    elif any(keyword in item for keyword in ['chicken', 'turkey', 'poultry']):
        return 'Poultry'
    elif 'egg' in item:
        return 'Eggs'
    elif 'fish' in item or 'shellfish' in item or 'seafood' in item:
        return 'Fish'
    elif any(keyword in item for keyword in ['legume', 'bean', 'lentil', 'pea']):
        return 'Legumes'
    elif 'spice' in item or 'herb' in item or 'sauce' in item or 'seasoning' in item:
        return 'Condiments and sauces'
    elif any(keyword in item for keyword in ['sugar', 'sweet', 'candy', 'snack', 'chocolate']):
        return 'Sweets and snacks'
    elif any(keyword in item for keyword in ['beverage', 'juice', 'coffee', 'tea', 'drink']):
        return 'Beverages'
    else:
        return 'Miscellaneous'

# Apply the classification function to categorize based on 'Matvare'
combined_df['Categories'] = combined_df['Matvare'].apply(classify_food)

# Group by custom categories and calculate the mean of the selected columns
category_averages_combined = combined_df.groupby('Categories').mean()

# Convert the water content to percent dry matter
combined_df['Percent Dry Matter'] = 100 - combined_df['Water (g)']

# Group by custom categories and calculate the mean of the selected columns, including Percent Dry Matter
category_averages_combined = combined_df.groupby('Categories').mean()

#Plotting the macros
fig, ax = plt.subplots(2, 1, figsize=(12, 16))

# Subplot 1: Protein, Fat, Carbohydrate, and Sugar
nutrients = ['Protein (g)', 'Fat (g)', 'Carbohydrate (g)', 'Sugar, total (g)']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
category_averages_combined[nutrients].plot(kind='bar', ax=ax[0], color=colors)
ax[0].set_title('Average Nutrient Content')
ax[0].set_xlabel('Food Category')
ax[0].set_ylabel('Average Content (g)/100g')
ax[0].legend(title='Nutrients')
ax[0].tick_params(axis='x', rotation=45)

# Subplot 2: Kilokalories
sns.barplot(x=category_averages_combined.index, y=category_averages_combined['Kilokalorier (kcal)'], ax=ax[1])
ax[1].set_title('Average Kilokalories per Category')
ax[1].set_xlabel('Custom Category')
ax[1].set_ylabel('Average Kilokalories (kcal) per 100g')
ax[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

# Export the results to auxiliary folder
output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary', 'food_composition.xlsx')
category_averages_combined.to_excel(output_path)


