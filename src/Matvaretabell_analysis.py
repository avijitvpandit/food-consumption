#%%

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

# Load the Excel file
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'matvaretabell', 'all-foods.xlsx')
xls = pd.ExcelFile(file_path)

# Load the required sheet
foods_nutrients_df = pd.read_excel(xls, sheet_name='Foods (all nutrients)')

# Step 1: Identify rows where 'Matvare ID' contains non-numeric values, which represent the main categories
foods_nutrients_df['IsMainCategory'] = foods_nutrients_df['Matvare ID'].apply(lambda x: not str(x).replace('.', '').isnumeric())

# Step 2: Forward-fill the main category names into a new 'Main Category' column
foods_nutrients_df['Main Category'] = foods_nutrients_df['Matvare ID'].where(foods_nutrients_df['IsMainCategory']).ffill()

# Step 3: Keep 'Matvare ID' in the cleaned DataFrame for debugging and traceability
foods_nutrients_cleaned = foods_nutrients_df[~foods_nutrients_df['IsMainCategory']]

# Select necessary columns for analysis, including 'Matvare ID' for debugging
nutrients_selected = foods_nutrients_cleaned[['Main Category', 'Matvare', 'Matvare ID', 'Protein (g)', 'Fat (g)', 'Carbohydrate (g)', 'Water (g)', 
                                              'Phosphorus (P) (mg)', 'Sugar, total (g)']]

# Merge with additional nutritional data if necessary (e.g., kilocalories)
foods_df = pd.read_excel(xls, sheet_name='Foods')
foods_selected = foods_df[['Matvare', 'Kilokalorier (kcal)', 'Spiselig del (%)']]

# Merge the two DataFrames (including 'Matvare ID' for traceability)
combined_df = pd.merge(nutrients_selected, foods_selected, on='Matvare', how='inner')

# Calculate percent dry matter
combined_df['Percent Dry Matter'] = 100 - combined_df['Water (g)']

# Step 4: Apply the category mapping
category_mapping = {
    'Fruit and berries': 'Fruits and nuts',
    'Nuts and seeds': 'Fruits and nuts',
    'Vegetables': 'Vegetables',
    'Potatoes': 'Starchy vegetables',
    'Cereals, bread and cakes': 'Grains and cereals',
    'Dairy products': 'Dairy and alternatives',
    'Meat and poultry': 'Red meat',  # This will handle the majority, we'll handle Poultry separately
    'Egg': 'Eggs',
    'Fish and shellfish': 'Fish',
    'Legumes': 'Legumes',
    'Herbs and spices': 'Condiments and sauces',
    'Sugar and sweet products': 'Sweets and snacks',
    'Beverages': 'Beverages',
    'Other foods and dishes': 'Miscellaneous',
    'Cooking fat': 'Miscellaneous',
    'Infant food': 'Miscellaneous'
}

# Step 5: Create a function to apply keyword-based classification for Red meat and Poultry within "Meat and poultry"
def classify_meat(item, category):
    if category == 'Meat and poultry':
        item = item.lower()
        if 'chicken' in item or 'poultry' in item or 'turkey' in item:
            return 'Poultry'
        else:
            return 'Red meat'
    return category

# Apply the classification for 'Meat and poultry'
combined_df['Main Category'] = combined_df.apply(lambda row: classify_meat(row['Matvare'], category_mapping.get(row['Main Category'], row['Main Category'])), axis=1)

# Group by 'Main Category' and calculate the mean values
category_averages_combined = combined_df.groupby('Main Category').mean()

# Drop the outlier row with "01.332" (if necessary, based on data inspection)
category_averages_combined = category_averages_combined[category_averages_combined.index != "01.332"]

# Final categories
final_categories = {
    'Fruits and nuts', 'Vegetables', 'Starchy vegetables', 'Grains and cereals', 
    'Dairy and alternatives', 'Red meat', 'Poultry', 'Eggs', 'Fish', 
    'Legumes', 'Condiments and sauces', 'Sweets and snacks', 'Beverages', 'Miscellaneous'
}

# Ensure the final categories are the only ones used
category_averages_combined = category_averages_combined[category_averages_combined.index.isin(final_categories)]

# Plotting the macros
fig, ax = plt.subplots(2, 1, figsize=(12, 16))

# Subplot 1: Protein, Fat, Carbohydrate, and Sugar
nutrients = ['Protein (g)', 'Fat (g)', 'Carbohydrate (g)', 'Sugar, total (g)']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
category_averages_combined[nutrients].plot(kind='bar', ax=ax[0], color=colors)
ax[0].set_title('Average Nutrient Content per Main Category')
ax[0].set_ylabel('Average Content (g)/100g')
ax[0].legend(title='Nutrients')
ax[0].tick_params(axis='x', rotation=45)
ax[0].set_xlabel('')  # Remove x-label

# Subplot 2: Kilocalories
sns.barplot(x=category_averages_combined.index, y=category_averages_combined['Kilokalorier (kcal)'], ax=ax[1])
ax[1].set_title('Average Kilocalories per Main Category')
ax[1].set_ylabel('Average Kilocalories (kcal) per 100g')
ax[1].tick_params(axis='x', rotation=45)
ax[1].set_xlabel('')  # Remove x-label

plt.tight_layout()
plt.show()

# Export the results to an Excel file
output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary', 'food_composition.xlsx')
category_averages_combined.to_excel(output_path)
