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
df_nutrient_totals = pd.merge(nutrients_selected, foods_selected, on='Matvare', how='inner')

# Calculate percent dry matter
df_nutrient_totals['Percent Dry Matter'] = 100 - df_nutrient_totals['Water (g)']

# Rename 'Main Category' to 'FoodCategory' for clarity
df_nutrient_totals.rename(columns={'Main Category': 'FoodCategory'}, inplace=True)

# Updated category mapping
category_mapping = {
    'Fruit and berries': 'Vegetables, Fruits and nuts',
    'Nuts and seeds': 'Vegetables, Fruits and nuts',
    'Vegetables': 'Vegetables, Fruits and nuts',
    'Potatoes': 'Starchy vegetables',
    'Cereals, bread and cakes': 'Grains, cereals and legumes',
    'Dairy products': 'Dairy and egg',
    'Meat and poultry': 'Red meat',  # We'll handle poultry separately using the classify_meat function
    'Egg': 'Dairy and egg',
    'Fish and shellfish': 'Fish',
    'Legumes': 'Grains, cereals and legumes',
    'Herbs and spices': 'Miscellaneous',
    'Sugar and sweet products': 'Sweets and snacks',
    'Beverages': 'Beverages',
    'Other foods and dishes': 'Miscellaneous',
    'Cooking fat': 'Fats and oils',
    'Infant food': 'Miscellaneous'
}
#%%
# Function to classify poultry separately from red meat within the 'Meat and poultry' category
def classify_meat(item, category):
    # If the category is "Red meat", we classify it based on keywords for poultry
    if category == 'Red meat':
        item_lower = item.lower()
        if 'chicken' in item_lower or 'poultry' in item_lower or 'turkey' in item_lower or 'hen' in item_lower or 'duck' in item_lower:
            return 'Poultry'  # Reclassify as Poultry if these keywords are found
        else:
            return 'Red meat'  # Explicitly return 'Red meat' if no poultry keywords are found
    return category  # Otherwise, keep the category as-is

# Map 'FoodCategory' to new categories using 'category_mapping'
df_nutrient_totals['Category'] = df_nutrient_totals['FoodCategory'].map(category_mapping)
# If any 'FoodCategory' is not in 'category_mapping', keep the original
df_nutrient_totals['Category'] = df_nutrient_totals['Category'].fillna(df_nutrient_totals['FoodCategory'])

# Applying the classification to the DataFrame correctly
df_nutrient_totals['Category'] = df_nutrient_totals.apply(
    lambda row: classify_meat(row['Matvare'], row['Category']),
    axis=1
)

# Check if poultry is classified correctly
print("Sample of Poultry items:")
print(df_nutrient_totals[df_nutrient_totals['Category'] == 'Poultry'][['Matvare', 'Category']].head())

print("Sample of Red meat items:")
print(df_nutrient_totals[df_nutrient_totals['Category'] == 'Red meat'][['Matvare', 'Category']].head())

# Group the data by the new 'Category' and recalculate the average nutrient values
category_averages_combined = df_nutrient_totals.groupby('Category').mean()

#'01.332' is an outlier:
category_averages_combined.drop('01.332 ', inplace=True)
#Rename Category to FoodCategory
category_averages_combined.rename(index={'FoodCategory': 'Category'}, inplace=True)

# Export the results to an Excel file
output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary', 'food_composition.xlsx')
category_averages_combined.to_excel(output_path)

# Print the unique categories to ensure Poultry and Red meat are correctly separated
print("Unique categories after classification:", df_nutrient_totals['Category'].unique())

# Plotting the macros
fig, ax = plt.subplots(2, 1, figsize=(12, 16))

# Subplot 1: Protein, Fat, Carbohydrate, and Sugar
nutrients = ['Protein (g)', 'Fat (g)', 'Carbohydrate (g)', 'Sugar, total (g)']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
category_averages_combined[nutrients].plot(kind='bar', ax=ax[0], color=colors)
ax[0].set_title('Average Nutrient Content per Main Category')
ax[0].set_xlabel('')
ax[0].set_ylabel('Average Content (g)/100g')
ax[0].legend(title='Nutrients')
ax[0].tick_params(axis='x', rotation=45)

# Subplot 2: Kilocalories
sns.barplot(x=category_averages_combined.index, y=category_averages_combined['Kilokalorier (kcal)'], ax=ax[1])
ax[1].set_title('Average Kilocalories per Main Category')
ax[1].set_xlabel('')
ax[1].set_ylabel('Average Kilocalories (kcal) per 100g')
ax[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

# %%
