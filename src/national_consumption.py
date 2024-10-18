#%%importing the relevant libraries
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#%%
# Load the excel file from Helsedirektoratet folder in raw
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'Helsedirektoratet')
filename = 'national consumption.xlsx'
df = pd.read_excel(os.path.join(file_path, filename))
# drop the last three rows
df.drop(df.tail(3).index, inplace=True)
#Keep only the last 5 rows as they contain data for the years 2019, 2020, 2021, 2022, 2023
df = df.tail(5)

#%%
# Print all the column names to map with the study categories

category_mapping_new = {
    'Korn, som mel': 'Grains and cereals',  # Grain products
    'Ris, gryn og mel': 'Grains and cereals',  # Rice, grains, and flour
    'Poteter, friske': 'Starchy vegetables',  # Fresh potatoes
    'Potetprodukter': 'Starchy vegetables',  # Potato products (processed)
    'Potetmel': 'Starchy vegetables',  # Potato starch
    'Sukker/sukkervarer': 'Sweets and snacks',  # Sugar and confectionery
    'Erter/nøtter/kakao': 'Legumes',  # Peas, nuts, and cocoa (mainly focusing on peas and nuts)
    'Kakaoprodukter': 'Sweets and snacks',  # Cocoa products (e.g., chocolate)
    'Grønnsaker': 'Vegetables',  # Vegetables
    'Frukt og bær': 'Fruits and nuts',  # Fruits and berries
    'Kjøtt': 'Red meat',  # Meat (generic, includes red meat)
    'Kjøttbiprodukter': 'Red meat',  # Meat by-products (assumed to be from red meat)
    'Egg': 'Eggs',  # Eggs
    'Fisk': 'Fish',  # Fish
    'Helmelk': 'Dairy and alternatives',  # Whole milk
    'Lettmelk': 'Dairy and alternatives',  # Low-fat milk
    'Skummet melk': 'Dairy and alternatives',  # Skimmed milk
    'Yoghurt': 'Dairy and alternatives',  # Yogurt
    'Melkeprodukter': 'Dairy and alternatives',  # Dairy products
    'Fløte, rømme (38%)': 'Dairy and alternatives',  # Cream and sour cream (38% fat)
    'Ost': 'Dairy and alternatives',  # Cheese
    'Smør': 'Fats and oils',  # Butter
    'Margarin': 'Fats and oils',  # Margarine
    'Herav lettmargarin': 'Fats and oils',  # Light margarine
    'Annet fett': 'Fats and oils',  # Other fats (unspecified)
    'Uspesifisert handel': 'Miscellaneous',  # Unspecified trade
    'Grensehandel': 'Miscellaneous'  # Border trade (unspecified)
}

# Applying the mapping to the dataframe columns
df_mapped = df.rename(columns=category_mapping_new)
# Summing columns within the same category
grouped_df = df_mapped.groupby(axis=1, level=0).sum()
grouped_df['Year'] = df['Year']  # Add back the 'Year' column
grouped_df.set_index('Year', inplace=True)
# Calculate the average consumption for each category over the years
average_consumption = grouped_df.mean()

# Add the average consumption as a new row in the grouped_df
grouped_df.loc['Average'] = average_consumption
print("Average consumption over the years:")
print(average_consumption)
#%%
#%%
# Load the Excel file for individual consumption data
individual_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'helsedirektoratet', 'individual consumption.xlsx')
individual_df = pd.read_excel(individual_file_path)

# Drop the first 5 rows
individual_df.drop(individual_df.head(5).index, inplace=True)

# Reset the index
individual_df.reset_index(drop=True, inplace=True)

# Define the category mapping for individual data
individual_category_mapping = {
    'Korn, som mel (inkl. ris)': 'Grains and cereals',
    'Matpoteter': 'Starchy vegetables',
    'Poteter til bearbeiding': 'Starchy vegetables',
    'Grønnsaker': 'Vegetables',
    'Frukt og bær': 'Fruits and nuts',
    'Kjøtt og kjøttbiprodukter': 'Red meat',
    'Fisk (hel urenset rund vekt)': 'Fish',
    'Egg': 'Eggs',
    'Helmelk': 'Dairy and alternatives',
    'Lettmelk': 'Dairy and alternatives',
    'Mager melk2': 'Dairy and alternatives',
    'Yoghurt': 'Dairy and alternatives',
    'Konserverte melkeprodukter': 'Dairy and alternatives',
    'Fløte, rømme': 'Dairy and alternatives',
    'Ost': 'Dairy and alternatives',
    'Smør': 'Fats and oils',
    'Margarin': 'Fats and oils',
    'Sukker': 'Sweets and snacks'
}

# Rename the columns using the individual category mapping
individual_df_renamed = individual_df.rename(columns=individual_category_mapping)

# Group columns by category and sum their values for each year
individual_grouped_df = individual_df_renamed.groupby(axis=1, level=0).sum()

# Assuming 'Year' is a column in individual_df_renamed, set it as the index
individual_grouped_df['Year'] = individual_df_renamed['Year']
individual_grouped_df.set_index('Year', inplace=True)

# Add the row for average consumption
individual_average_consumption = individual_grouped_df.mean()
individual_grouped_df.loc['Average'] = individual_average_consumption

# Display the remapped and grouped DataFrame
print("Grouped Data by Categories (Individual Consumption):")
print(individual_grouped_df.head())

#%%
# Comparison with upscaled values from human balance
# Load the Excel file
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary', 'average consumption.xlsx')
norkost_df = pd.read_excel(file_path)
norkost_df.head()

#Create a df that contains average consumption of all age groups 
norkost_df_avg = norkost_df.groupby('FoodCategory').mean().reset_index()
norkost_df_avg.set_index('FoodCategory', inplace=True)
norkost_df_avg = norkost_df_avg[[ 'Average amount consumed (g)']]
norkost_df_avg.rename(columns={'Average amount consumed (g)': 'Average'}, inplace=True)
#convert from gms to kg
norkost_df_avg['Average'] /= 1000
# Convert to yearly consumption by multiplying with 365
norkost_df_avg['Average'] *= 365

# Multiply with the Norwegian population to upscale the values
norwegian_population = 4.8e6  # 4.8 million
norkost_upscaled = norkost_df_avg.copy()
norkost_upscaled['Average'] *= norwegian_population
# convert from grams to 1000 tons
norkost_upscaled['Average'] /= 1e6
# Transpose the DataFrame for easier comparison
norkost_upscaled = norkost_upscaled.T
norkost_upscaled
#%%
# Define colors for food groups
food_group_colors = {
    'Fruits and nuts': '#186a3b',
    'Vegetables': '#28b463',
    'Starchy vegetables': '#82e0aa',
    'Grains and cereals': '#abebc6',
    'Legumes': '#17a589',
    'Dairy and alternatives': '#e59866',
    'Red meat': '#d35400',
    'Poultry': '#dc7633',
    'Eggs': '#f5cba7',
    'Fish': '#3498db',
    'Fats and oils': '#eaecee',
    'Sweets and snacks': '#808b96',
    'Beverages': '#aab7b8',
    'Miscellaneous': '#34495e'
}

# Reorder the columns of individual_grouped_df to match the order of food_group_colors
ordered_columns = [col for col in food_group_colors.keys() if col in individual_grouped_df.columns]
individual_grouped_df = individual_grouped_df[ordered_columns]

# Create the stacked bar plot with custom colors for individual data
individual_grouped_df.drop('Average').plot(kind='bar', stacked=True, figsize=(10, 6), color=[food_group_colors.get(x, '#333333') for x in individual_grouped_df.columns])

# Customize the plot
plt.title('Individual Food Category Consumption Over Time')
plt.xlabel('Year')
plt.ylabel('Amount (kg per year per person)')
plt.legend(title='Food Categories', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()

# Create a new DataFrame to hold both datasets for comparison
comparison_df_individual = pd.DataFrame({
    'Helsedirektoratet Individual': individual_average_consumption,
    'Norkost Individual': norkost_df_avg['Average'],
})

# Plot the comparison for individual data
comparison_df_individual.plot(kind='bar', figsize=(12, 6), color=['#1f77b4', '#ff7f0e'])

# Customize the plot
plt.title('Comparison of Average Individual Food Consumption')
plt.xlabel('Food Categories')
plt.ylabel('Average Amount Consumed (kg per year per person)')
plt.legend(title='Source', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()

# %%
