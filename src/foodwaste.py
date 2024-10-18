#%%
import pandas as pd
import os
import matplotlib.pyplot as plt

# Step 1: Read the data from Excel
# Construct the file path using os.path.join for better compatibility across different operating systems
current_directory = os.path.dirname(__file__)
file_path = os.path.join(current_directory, '..', 'data', 'raw', 'matsvinn', 'matsvinn.xlsx')
df = pd.read_excel(file_path, sheet_name=None)  # Load all sheets into a dictionary

# Assuming the sheet names are 'Food Industry', 'Wholesaler', 'Retailer', 'Household'
df_food_industry = df['Food Industry']
df_wholesaler = df['Wholesaler']
df_retailer = df['Retailer']
df_household = df['Household']
#%%
# Step 2: Category mapping based on the provided final categories
category_mapping = {
    'Bakervarer': 'Grains and cereals',
    'Langtidsholdbart': 'Miscellaneous',
    'Drikkevarer': 'Beverages',
    'Frisk frukt og grønt': 'Vegetables',
    'Meierivarer': 'Dairy and alternatives',
    'Egg': 'Eggs',
    'Frossen mat': 'Miscellaneous',
    'Ferdigmat og deli': 'Miscellaneous',
    'Kjøttvarer': 'Red meat',
    'Øvrig': 'Miscellaneous',
    'Gryte- og tallerkenrester': 'Miscellaneous',  # From household data
    'Diverse rester': 'Miscellaneous',  # From household data
    'Brød og andre bakervarer': 'Grains and cereals',  # From household data
    'Meieriprodukter': 'Dairy and alternatives',  # From household data
    'Kjøtt': 'Red meat',  # From household data
    'Fisk': 'Fish',  # From household data
    'Frukt og grønnsaker': 'Vegetables'  # From household data
}

# Step 4: Calculate the average across the years for each stage
def calculate_avg_by_category(df, category_mapping):
    # Map the columns to the relevant categories
    df_mapped = df.rename(columns=category_mapping)
    
    # Ensure that all columns are numeric
    df_mapped = df_mapped.apply(pd.to_numeric, errors='coerce')
    
    # Calculate the average across the years (excluding 'Year' if it exists)
    df_avg = df_mapped.mean(axis=0)
    
    return df_avg

# Calculate the average for each stage
df_food_industry_avg = calculate_avg_by_category(df_food_industry, category_mapping)
df_wholesaler_avg = calculate_avg_by_category(df_wholesaler, category_mapping)
df_retailer_avg = calculate_avg_by_category(df_retailer, category_mapping)

# Reshape the household data (assuming it's structured differently)
df_household_cleaned = df_household.set_index('Type Mat').T  # Transpose the data
df_household_grouped = df_household_cleaned.rename(columns=category_mapping)

# Step 5: Remove total/aggregate columns and adjust household data for total population
df_household_grouped = df_household_grouped.loc[:, ~df_household_grouped.columns.str.contains('|'.join(columns_to_remove), case=False)]
population_of_norway = 5_367_580  # Approximate population of Norway
households_in_norway = population_of_norway / 2  # Two people per household
df_household_grouped = df_household_grouped.sum() * households_in_norway / 1_000  # Convert kg to tons
#%%
# Start with the Food Industry as the base DataFrame
df_combined_avg = df_food_industry_avg.to_frame(name='Food Industry')

# Join with Wholesaler data
df_combined_avg = df_combined_avg.join(df_wholesaler_avg.to_frame(name='Wholesaler'), how='outer')

# Join with Retailer data
df_combined_avg = df_combined_avg.join(df_retailer_avg.to_frame(name='Retailer'), how='outer')

# Join with Household data
df_combined_avg = df_combined_avg.join(df_household_grouped.to_frame(name='Household'), how='outer')

#Fill na with 0
df_combined_avg.fillna(0, inplace=True)

# Drop the rows 'Total Waste (tons)' and 'Year'
df_combined_avg.drop(index=['Total Waste (tons)', 'Year'], inplace=True, errors='ignore')
# Drop rows with duplicate index names
df_combined_avg = df_combined_avg[~df_combined_avg.index.duplicated(keep='first')]

#%%
# Step 6: Plot the data as a stacked bar chart
food_group_colors = {
    'Grains and cereals': '#abebc6',
    'Miscellaneous': '#34495e',
    'Beverages': '#aab7b8',
    'Vegetables': '#28b463',
    'Dairy and alternatives': '#e59866',
    'Eggs': '#f5cba7',
    'Red meat': '#d35400',
    'Fish': '#3498db'
}

# Ensure the colors match the categories in the DataFrame
colors = [food_group_colors.get(category, '#000000') for category in df_combined_avg.index]

# Plotting
ax = df_combined_avg.T.plot(kind='bar', stacked=True, color=colors, figsize=(12, 8))

# Adding labels and title
ax.set_xlabel('Stage')
ax.set_ylabel('Average Food Waste (tons)')
ax.set_title('Average Food Waste by Stage and Category')
ax.legend(title='Food Category', bbox_to_anchor=(1.05, 1), loc='upper left')

# Show plot
plt.tight_layout()
plt.show()
# %%
