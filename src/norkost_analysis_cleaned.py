# In the first section of this file Norkost 3 is loaded and analysed 
#%% 
# Importing the libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os
from plot_functions import (
    plot_energy_distribution,
    plot_energy_by_age_group,
    plot_average_consumption_by_gender,
    plot_average_consumption_by_age_group,
    plot_population_pyramid
)

#%%
# EXPLANATION OF THE FILE 
# SECTION 1 : Norkost 3 
# In the first section of this file Norkost 3 is loaded and cleaned 
# There are 2 main parts - ENERGY and FOOD GROUPS 
# ENERGY calculates the total energy consumption and groups by age and gender
# FOOD GROUPS maps the existing to right food categories 


# Then norkost 2 is loaded, cleaned and exported 
# They both are merged later and exported as one file to the auxillary data folder
# g/day for 14 categories in nk3 and for xx categories in nk2 
# Then the calories, protein, carbohydrates, fats and total Dry matter are calculated 
# using the matvaretabellen 

# NOTE : The calories calculated from matvaretabellen 
# and calories from nk survey have a big discrepancy
# TODO : Talk to NK lady and ask for g/ day 
# to calories/day conversion key for food categories 

#%% 
# SECTION 1 : Norkost 3 
# Load and clean the data for NORKOST 3
path = os.path.join('..', 'data', 'raw', 'norkost')
file_name = 'Norkost 3-data til NTNU.xlsx'
file_path = os.path.join(path, file_name)
background_sheet = 'Bakgrunnsvariabler'
foodgroups_sheet = 'Matvaregrupper'
energy_sheet = 'Stoffer u tilskudd'
df_background = pd.read_excel(file_path, sheet_name=background_sheet)
df_food_groups = pd.read_excel(file_path, sheet_name=foodgroups_sheet, header=2)
df_energy = pd.read_excel(file_path, sheet_name=energy_sheet, header=None)

# Cleaning the background data
df_background = df_background.iloc[:, :-3]  # Drop the last three columns
df_background.drop(columns=['Hushold1'], inplace=True)  # Drop the household column
df_background.rename(columns={'Nr': 'ID'}, inplace=True)  # Rename 'Nr' to 'ID'
df_background.rename(columns={
    "Alder": "Age",
    "Utdann1": "Education",
    "Kjønn": "Gender",
    "Landsdel": "Region"
}, inplace=True)  # Rename columns
df_background['Education'] = df_background['Education'].map({
    0: "None",
    1: "Primary school",
    2: "Middle school",
    3: "High school",
    4: "Higher secondary",
    5: "Vocational training",
    6: "Undergraduate",
    7: "Postgraduate",
    9: "Unanswered"
})
#%%
#### ENERGY #####
#Cleaning the energy data
df_energy = df_energy.iloc[3:].reset_index(drop=True)
df_energy.columns = df_energy.iloc[0]  # Set the correct header
df_energy = df_energy[['Nr', 'Energi']]  # Only keep 'Nr' and 'Energi' columns
df_energy = df_energy.drop(0)  # Drop the first row
df_energy.rename(columns={'Nr': 'ID', 'Energi': 'Energy'}, inplace=True)
df_energy = df_energy.drop(1)  # Drop the second row (if necessary)
df_energy.reset_index(drop=True, inplace=True)  # Reset the index
df_energy['Energy'] = pd.to_numeric(df_energy['Energy'], errors='coerce') / 4.184  # Convert KJ to Kcal
# Merge df_background and df_energy
df_energy_m = pd.merge(df_energy, df_background, on='ID')
# Map gender numeric values to strings
df_energy_m['Gender'] = df_energy_m['Gender'].map({1: 'Male', 2: 'Female'})
# Calculate mean and standard deviation for each gender
mean_energy_male = df_energy_m[df_energy_m['Gender'] == 'Male']['Energy'].mean()
std_energy_male = df_energy_m[df_energy_m['Gender'] == 'Male']['Energy'].std()
mean_energy_female = df_energy_m[df_energy_m['Gender'] == 'Female']['Energy'].mean()
std_energy_female = df_energy_m[df_energy_m['Gender'] == 'Female']['Energy'].std()
# Create 10-year age groups
df_energy_m['AgeGroup'] = pd.cut(
    df_energy_m['Age'],
    bins=range(0, 101, 10),
    right=False,
    labels=[f'{i}-{i+9}' for i in range(0, 100, 10)]
)
# PLOTS - ENERGY 
# Plot energy distribution by mean energy intake for each gender
# Plot energy intake by age group and gender
# Create the 'visualizations' directory if it doesn't exist
visualizations_dir = os.path.join('..', 'visualizations')
os.makedirs(visualizations_dir, exist_ok=True)

# Save the plots
energy_by_age_group_plot_path = os.path.join(visualizations_dir, 'energy_by_age_group.png')
plt.figure()
plot_energy_by_age_group(df_energy_m)
plt.savefig(energy_by_age_group_plot_path)
plt.close()

average_consumption_by_gender_plot_path = os.path.join(visualizations_dir, 'average_consumption_by_gender.png')
plt.figure()
plot_energy_distribution(df_energy_m, mean_energy_male, std_energy_male, mean_energy_female, std_energy_female)
plt.savefig(average_consumption_by_gender_plot_path)
plt.close()
#%%
#### FOOD GROUPS ######
#Cleaning the food groups data
df_food_groups = df_food_groups.dropna(how='all').reset_index(drop=True)  # Drop any fully empty rows
df_food_groups = df_food_groups.dropna(axis=1, how='all')  # Drop any fully empty columns
df_food_groups.rename(columns={'Nr': 'ID'}, inplace=True)
# Handle NaN values in ID column by converting to numeric and dropping rows with NaN IDs
df_food_groups['ID'] = pd.to_numeric(df_food_groups['ID'], errors='coerce')
df_food_groups = df_food_groups.dropna(subset=['ID'])
df_food_groups['ID'] = df_food_groups['ID'].astype(int)
# Ensure that 'TOTALT' column exists and is numeric
df_food_groups['TOTALT'] = pd.to_numeric(df_food_groups['TOTALT'], errors='coerce').fillna(0)
# Mapping the food groups to the correct category
food_group_mapping = {
    'Vegetables, fruits and nuts': [
        'FRUKTB', # fruits
        'GRS_FF','GRS_BL','GRS_U', 'GRS_K', #Vegetables 
        'POTET', # Potatoes
    ],
    'Grains, cereals and legumes': [
        'BROD', 'KORNPR', 'KAKER',   # Cereals
        'BELGFR' # Legumes
    ],
    'Dairy and egg': [
        'MELKYO',  'OST', # Milk and cheese 
        'EGG',
    ],
    'Red meat': [
        'KJOT_R',
        'KJOT_U', 'KJOT_M', 'KJOT_S', 'KJOT_P', 'KJO_AF',
        'KJO_PL', 'KJO_AP', 'KJORET', 'BLODIN'
    ],
    'Poultry': [
        'KJOT_HV'
    ],
    'Fish': [
        'FISK'
    ],
    'Sweets and snacks': [
        'SUKSOT'
    ],
    'Beverages': [
        'DRIKKE'
    ],
    'Fats and oils': [
        'SMARGO'
    ],
    'Miscellaneous': [
        'DIVERS'
    ]
}
# Create a reverse mapping from food group codes to categories
#Reverse mapping using dictionary comprehension
reverse_food_group_mapping = {code: category for category, codes in food_group_mapping.items() for code in codes}

# Reshape the DataFrame to a long format
df_long = df_food_groups.melt(id_vars=['ID', 'TOTALT'], var_name='FoodGroup', value_name='Amount')
df_long['Category'] = df_long['FoodGroup'].map(reverse_food_group_mapping)
# Ensure 'Amount' is numeric and handle NaN values
df_long['Amount'] = pd.to_numeric(df_long['Amount'], errors='coerce').fillna(0)
# Calculate the total amount of food consumed per category
df_food = df_long.groupby(['ID', 'Category'])['Amount'].sum().reset_index()
df_food = df_food.pivot(index='ID', columns='Category', values='Amount').reset_index()
df_food = pd.merge(df_background[['ID', 'Age', 'Gender', 'Education', 'Region']], df_food, on='ID', how='left')
df_food['Gender'] = df_food['Gender'].map({1: 'Male', 2: 'Female'})
categories = [c for c in df_food.columns if c not in ['ID', 'Age', 'Gender', 'Education', 'AgeGroup', 'Region', 'TotalConsumption']]
categories = categories[1:]
average_consumption = df_food.groupby('Gender')[categories].mean().T
# Create 10-year age groups in df_food
df_food['AgeGroup'] = pd.cut(
    df_food['Age'],
    bins=range(0, 101, 10),
    right=False,
    labels=[f'{i}-{i+9}' for i in range(0, 100, 10)]
)

average_consumption_age_group = df_food.groupby('AgeGroup')[categories].mean().T
average_consumption_age_group.dropna(axis=1, inplace=True)
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
    'Miscellaneous': '#34495e'
}
# Reshape the DataFrame to a long format
df_long = df_food_groups.melt(id_vars=['ID', 'TOTALT'], var_name='FoodGroup', value_name='Amount')

# Map the food group codes to categories
df_long['Category'] = df_long['FoodGroup'].map(reverse_food_group_mapping)

# Identify unmapped food group codes
unmapped_codes = df_long[df_long['Category'].isnull()]['FoodGroup'].unique()
if len(unmapped_codes) > 0:
    print(f"Unmapped food group codes: {unmapped_codes}")
else:
    print("All food group codes are mapped successfully.")

# Ensure 'Amount' is numeric and handle NaN values
df_long['Amount'] = pd.to_numeric(df_long['Amount'], errors='coerce').fillna(0)

# Calculate the total amount of food consumed per category
df_food = df_long.groupby(['ID', 'Category'])['Amount'].sum().reset_index()

# Pivot to wide format
df_food = df_food.pivot(index='ID', columns='Category', values='Amount').reset_index()

# Merge with background data including Region
df_food = pd.merge(df_background[['ID', 'Age', 'Gender', 'Education', 'Region']], df_food, on='ID', how='left')

# Map gender numeric values to strings
df_food['Gender'] = df_food['Gender'].map({1: 'Male', 2: 'Female'})

#%% Verify the aggregation by comparing total consumption
# Calculate total consumption from aggregated categories
category_columns = df_food.columns.difference(['ID', 'Age', 'Gender', 'Education', 'Region'])
df_food['TotalConsumption'] = df_food[category_columns].sum(axis=1)

# Retrieve original total consumption from df_food_groups
original_totals = df_food_groups[['ID', 'TOTALT']].drop_duplicates()

# Merge and compare totals
comparison = pd.merge(df_food[['ID', 'TotalConsumption']], original_totals, on='ID')
comparison['Difference'] = comparison['TOTALT'] - comparison['TotalConsumption']

# Check the maximum difference
max_difference = comparison['Difference'].abs().max()
print(f"Maximum difference in total consumption: {max_difference}")

# If the maximum difference is significant, investigate further
if max_difference > 5000:
    discrepancies = comparison[comparison['Difference'] != 0]
    print("Discrepancies found in the following IDs:")
    print(discrepancies)
    # You may decide to adjust the mapping or handle specific cases

#%% Handle missing values in df_food
# Replace NaN values in category columns with 0
df_food[category_columns] = df_food[category_columns].fillna(0)

# Now recalculate 'TotalConsumption' after filling NaNs
df_food['TotalConsumption'] = df_food[category_columns].sum(axis=1)

# Re-compare totals
comparison = pd.merge(df_food[['ID', 'TotalConsumption']], original_totals, on='ID')
comparison['Difference'] = comparison['TOTALT'] - comparison['TotalConsumption']

# Recheck the maximum difference
max_difference = comparison['Difference'].abs().max()
print(f"Maximum difference after handling NaNs: {max_difference}")

#%% Plotting average consumption by gender and food categories
# Update the list of categories (exclude 'ID', 'Age', etc.)
categories = [c for c in df_food.columns if c not in ['ID', 'Age', 'Gender', 'Education', 'AgeGroup', 'Region', 'TotalConsumption']]

# Drop the beverages from the categories list
categories = categories[1:]

# Calculate average consumption by gender
average_consumption = df_food.groupby('Gender')[categories].mean().T

# Plot average consumption by gender
average_consumption.plot(kind='bar', figsize=(14, 8), color=['pink', 'blue'])
plt.title('Average Consumption by Food Category and Gender')
plt.xlabel('Food Category')
plt.ylabel('Average Amount Consumed (g)')
plt.legend(title='Gender')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

#%% Create 10-year age groups in df_food
df_food['AgeGroup'] = pd.cut(
    df_food['Age'],
    bins=range(0, 101, 10),
    right=False,
    labels=[f'{i}-{i+9}' for i in range(0, 100, 10)]
)

# Calculate average consumption by age group
average_consumption_age_group = df_food.groupby('AgeGroup')[categories].mean().T

# Drop the columns with NaN values (if any)
average_consumption_age_group.dropna(axis=1, inplace=True)

# Define colors for each food group (adjust as needed)
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

# Ensure the colors are applied in the correct order
colors = [food_group_colors.get(category, '#333333') for category in average_consumption_age_group.index]

# Plot average consumption by age group
average_consumption_age_group.T.plot(kind='barh', stacked=True, figsize=(14, 8), color=colors)
plt.title('Average Consumption by Food Category and Age Group')
plt.xlabel('Average Amount Consumed (g)')
plt.ylabel('Age Group')
plt.legend(title='Food Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Calculate average consumption by education
average_consumption_education = df_food.groupby('Education')[categories].mean().T

# Drop the columns with NaN values (if any)
average_consumption_education.dropna(axis=1, inplace=True)

# Plot average consumption by education
# Plot average consumption by education as a stacked barh chart
average_consumption_education.T.plot(kind='barh', stacked=True, figsize=(14, 8), color=colors)
plt.title('Average Consumption by Food Category and Education')
plt.xlabel('Average Amount Consumed (g)')
plt.ylabel('Education Level')
plt.legend(title='', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

#%% Export a table with average consumption by gender, age group, and food category
average_consumption_gender_age = df_food.groupby(['Gender', 'AgeGroup'])[categories].mean().reset_index()

# Melt the DataFrame to long format
average_consumption_gender_age_long = average_consumption_gender_age.melt(
    id_vars=['Gender', 'AgeGroup'],
    var_name='FoodCategory',
    value_name='Average amount consumed (g)'
)

# Fill NaN values with 0
average_consumption_gender_age_long['Average amount consumed (g)'].fillna(0, inplace=True)


#%% Import the food composition data
food_composition_path = os.path.join('..', 'data', 'auxiliary', 'food_composition.xlsx')
df_food_composition = pd.read_excel(food_composition_path)

# Rename the index column to 'FoodCategory' to match
df_food_composition.rename(columns={'Category': 'FoodCategory'}, inplace=True)

# merge average_consumption_gender_age_long with df_food_composition
# Merge average_consumption_gender_age_long with df_food_composition
average_consumption_gender_age_long = pd.merge(
    average_consumption_gender_age_long,
    df_food_composition,
    on='FoodCategory',
    how='left'
)

# Check if all FoodCategory values in average_consumption_gender_age_long are present in df_food_composition
missing_categories = average_consumption_gender_age_long[average_consumption_gender_age_long['Percent Dry Matter'].isnull()]['FoodCategory'].unique()
if len(missing_categories) > 0:
    print(f"Missing food categories in composition data: {missing_categories}")
else:
    print("All food categories are present in the composition data.")
#%%
# Calculate the nutrient totals
average_consumption_gender_age_long['TotalDryMatter'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['Percent Dry Matter'] / 100
)

average_consumption_gender_age_long['TotalFat'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['Fat (g)'] / 100
)

average_consumption_gender_age_long['TotalProtein'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['Protein (g)'] / 100
)

average_consumption_gender_age_long['TotalCarbohydrates'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['Carbohydrate (g)'] / 100
)

# TotalCalories calculation
average_consumption_gender_age_long['TotalCalories'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['Kilokalorier (kcal)'] / 100
)

# Total phosphorus calculation
average_consumption_gender_age_long['TotalPhosphorus'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['Phosphorus (P) (mg)'] / 100
)

# Drop the colums that are not needed
average_consumption_gender_age_long.drop(columns=[
    'Percent Dry Matter', 'Fat (g)', 'Protein (g)', 'Carbohydrate (g)', 'Kilokalorier (kcal)', 'Phosphorus (P) (mg)'
], inplace=True)

# Merge df_energy_long with average_consumption_gender_age_long
average_consumption_gender_age_long = pd.merge(
    average_consumption_gender_age_long,
    df_energy_long,
    on=['Gender', 'AgeGroup'],
    how='left'
)

#%% 
#Group by Gender, AgeGroup, and FoodCategory to calculate the total amount of each nutrient
df_nutrient_totals = average_consumption_gender_age_long.groupby(['Gender', 'AgeGroup', 'FoodCategory']).agg({
    'TotalDryMatter': 'sum',
    'TotalFat': 'sum',
    'TotalProtein': 'sum',
    'TotalCarbohydrates': 'sum',
    'TotalCalories': 'sum',
    'TotalPhosphorus': 'sum',
    'Average amount consumed (g)': 'sum'
}).reset_index()

# Drop rows where TotalCalories is 0
df_nutrient_totals = df_nutrient_totals[df_nutrient_totals['TotalCalories'] > 0].reset_index(drop=True)

# Merge df_nutrient_totals with df_energy_long 
df_nutrient_totals = pd.merge(
    df_nutrient_totals,
    df_energy_long,
    on=['Gender', 'AgeGroup'],
    how='left'
)

# Export the df_nutrient_totals to an Excel file in auxillary folder
output_path = os.path.join('..', 'data', 'auxillary', 'average percapita consumption_nk3.xlsx')
df_nutrient_totals.to_excel(output_path, index=False)
print(f"Average consumption by gender and age group has been exported to {output_path}")



#%%
#data analysis for vegetarians
# Identify vegetarians based on df_nutrient_totals
# Define the food categories that are considered non-vegetarian
non_vegetarian_categories = [
    'Red meat', 'Poultry', 'Fish',
]

# Identify vegetarians based on the absence of non-vegetarian food categories
df_vegetarians = df_food[df_food[non_vegetarian_categories].sum(axis=1) == 0]

# Print the number of vegetarians 
num_vegetarians = len(df_vegetarians)
print(f"Number of vegetarians: {num_vegetarians}")

#%%
# SECTION 3 : NORKOST 2  
#%% Norkost 2 data analysis
# importing the Norkost 2 data 
path = os.path.join('..', 'data', 'raw', 'norkost')
file_name = 'Norkost 2.xlsx'
file_path = os.path.join(path, file_name)
df_norkost2 = pd.read_excel(file_path)
# Cleaning the data
#rename the row with age group 16-19 as 10 -19 
df_norkost2.loc[df_norkost2['Age group'] == '16-19', 'Age group'] = '10-19'
# Convert energy to Kcal
df_norkost2['Energy intake (MJ/day)'] = df_norkost2['Energy intake (MJ/day)']*1000 / 4.184
#rename the column Energy intake (MJ/day) to Energy (kcal/day)
df_norkost2.rename(columns={'Energy intake (MJ/day)': 'Energy (kcal/day)'}, inplace=True)
#Separate into male and female
norkost2_male = df_norkost2[df_norkost2['Gender'] == 'Male']
norkost2_female = df_norkost2[df_norkost2['Gender'] == 'Female']

# Create df_norkost3_male and df_norkost3_female from df_nutrient_totals
df_norkost3_male = df_nutrient_totals[df_nutrient_totals['Gender'] == 'Male']
df_norkost3_female = df_nutrient_totals[df_nutrient_totals['Gender'] == 'Female']
# Group by AgeGroup and calculate the mean energy intake for each group
norkost3_male = df_norkost3_male.groupby('AgeGroup')['AverageEnergyIntake'].mean().reset_index()
#Drop the NaN values in the 'AverageEnergyIntake' column
norkost3_male = norkost3_male.dropna(subset=['AverageEnergyIntake'])
# Create the female table 
norkost3_female = df_norkost3_female.groupby('AgeGroup')['AverageEnergyIntake'].mean().reset_index()
#Drop the NaN values in the 'AverageEnergyIntake' column
norkost3_female = norkost3_female.dropna(subset=['AverageEnergyIntake'])
#%% Plotting changes in energy intake between Norkost 2 and Norkost 3
# Plot energy distribution for Norkost 2 and compare with Norkost 3 in separate subplots for Male and Female
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18, 8), sharey=True)

# Set the width of the bars
bar_width = 0.35

# Set positions of the bars on the x-axis for Norkost 3 and Norkost 2 for Male
r1 = np.arange(len(norkost3_male['AgeGroup']))
r2 = [x + bar_width for x in r1]

# Male subplot
axes[0].bar(r1, norkost3_male['AverageEnergyIntake'], color='blue', width=bar_width, edgecolor='grey', label='Norkost 3')
axes[0].bar(r2, norkost2_male['Energy (kcal/day)'], color='blue', width=bar_width, edgecolor='grey', hatch='//', label='Norkost 2')
axes[0].set_title('Male')
axes[0].set_xlabel('Age Group', fontweight='bold')
axes[0].set_xticks([r + bar_width/2 for r in range(len(norkost3_male['AgeGroup']))])
axes[0].set_xticklabels(norkost3_male['AgeGroup'])
axes[0].set_ylabel('Average Energy Intake (Kcal) per day')
axes[0].legend(title='Survey')

# Set positions of the bars on the x-axis for Norkost 3 and Norkost 2 for Female
r3 = np.arange(len(norkost3_female['AgeGroup']))
r4 = [x + bar_width for x in r3]

# Female subplot
axes[1].bar(r3, norkost3_female['AverageEnergyIntake'], color='pink', width=bar_width, edgecolor='grey', label='Norkost 3')
axes[1].bar(r4, norkost2_female['Energy (kcal/day)'], color='pink', width=bar_width, edgecolor='grey', hatch='//', label='Norkost 2')
axes[1].set_title('Female')
axes[1].set_xlabel('Age Group', fontweight='bold')
axes[1].set_xticks([r + bar_width/2 for r in range(len(norkost3_female['AgeGroup']))])
axes[1].set_xticklabels(norkost3_female['AgeGroup'])
axes[1].legend(title='Survey')

# Set a common title for the figure
fig.suptitle('Energy Intake by Age Group and Gender (Norkost 2 vs Norkost 3)')
plt.tight_layout()
plt.show()

#%% Norkost 2 vs 3 food products comparison
#Visualize a population pyramid for Norkost 2 and compare with Norkost 3
#See the Norkkos 2 data
df_norkost2.head()
# Identify the columns in df_norkost2 that correspond to food categories
food_categories = df_food_composition['FoodCategory'].unique()
norkost2_categories = [col for col in df_norkost2.columns if col in food_categories]

# Rename 'Energy (kcal/day)' to 'AverageEnergyIntake'
df_norkost2.rename(columns={'Energy (kcal/day)': 'AverageEnergyIntake'}, inplace=True)

# Reshape df_norkost2 to long format
df_norkost2_long = df_norkost2.melt(
    id_vars=['Age group', 'Gender', 'AverageEnergyIntake'],
    value_vars=norkost2_categories,
    var_name='FoodCategory',
    value_name='Average amount consumed (g)'
)

#Rename Age group to AgeGroup
df_norkost2_long.rename(columns={'Age group': 'AgeGroup'}, inplace=True)

# Merge with food composition data
df_norkost2_long = pd.merge(
    df_norkost2_long,
    df_food_composition,
    on='FoodCategory',
    how='left'
)

# Calculate nutrient totals
df_norkost2_long['TotalCalories'] = (
    df_norkost2_long['Average amount consumed (g)'] *
    df_norkost2_long['Kilokalorier (kcal)'] / 100
)
df_norkost2_long['TotalDryMatter'] = (
    df_norkost2_long['Average amount consumed (g)'] *
    df_norkost2_long['Percent Dry Matter'] / 100
)
df_norkost2_long['TotalFat'] = (
    df_norkost2_long['Average amount consumed (g)'] *
    df_norkost2_long['Fat (g)'] / 100
)
df_norkost2_long['TotalProtein'] = (
    df_norkost2_long['Average amount consumed (g)'] *
    df_norkost2_long['Protein (g)'] / 100
)
df_norkost2_long['TotalCarbohydrates'] = (
    df_norkost2_long['Average amount consumed (g)'] *
    df_norkost2_long['Carbohydrate (g)'] / 100
)

#Group by Gender, AgeGroup, and FoodCategory to calculate the total amount of each nutrient
df_nutrient_totals_nk2 = df_norkost2_long.groupby(['Gender', 'AgeGroup', 'FoodCategory']).agg({
    'TotalDryMatter': 'sum',
    'TotalFat': 'sum',
    'TotalProtein': 'sum',
    'TotalCarbohydrates': 'sum',
    'TotalCalories': 'sum',
    'Average amount consumed (g)': 'sum',
    'AverageEnergyIntake': 'mean'
}).reset_index()

#using plot population pyramid function to plot the population pyramid for Norkost 2
plot_population_pyramid('TotalCalories', 'Total Calories (kcal)', food_group_colors, 'Norkost 2')
plot_population_pyramid('TotalProtein', 'Total Protein (g)', food_group_colors, 'Norkost 2')
plot_population_pyramid('TotalFat', 'Total Fat (g)',  food_group_colors, 'Norkost 2')
plot_population_pyramid('TotalCarbohydrates', 'Total Carbohydrates (g)', food_group_colors, 'Norkost 2')

#%%
# Export the df_nutrient_totals to an Excel file in auxillary folder
output_path = os.path.join('..', 'data', 'auxillary', 'average percapita consumption_nk2.xlsx')
df_nutrient_totals_nk2.to_excel(output_path, index=False)
print(f"Average consumption by gender and age group has been exported to {output_path}")


# %%
#