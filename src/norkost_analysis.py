
#%%importing the libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os


#%%
# Load and clean the data
path = os.path.join('..', 'data','raw', 'norkost')
file_name = 'Norkost 3-data til NTNU.xlsx'
file_path = os.path.join(path, file_name)
background_sheet = 'Bakgrunnsvariabler'
foodgroups_sheet = 'Matvaregrupper'
energy_sheet = 'Stoffer u tilskudd'
df_background = pd.read_excel(file_path, sheet_name=background_sheet)
df_food_groups = pd.read_excel(file_path, sheet_name=foodgroups_sheet, header=2)
df_energy = pd.read_excel(file_path, sheet_name=energy_sheet, header= None)

# Cleaning the background data

df_background = df_background.iloc[:, :-3]  # drop the last three columns
df_background.drop(columns=['Hushold1'], inplace=True)#drop the household column
df_background.rename(columns={'Nr': 'ID'}, inplace=True)  # rename Nr to ID
df_background.rename(columns={"Alder": "Age", "Utdann1": "Education", "Kjønn":"Gender","Landsdel":"Region"}, inplace=True)  # rename columns
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

# Cleaning the foodgroups data
df_food_groups = df_food_groups.dropna(how='all').reset_index(drop=True)  # Drop any fully empty rows
df_food_groups = df_food_groups.dropna(axis=1, how='all')  # Drop any fully empty columns
df_food_groups.rename(columns={'Nr': 'ID'}, inplace=True)

# Handle NaN values in ID column by converting to numeric and dropping rows with NaN IDs
df_food_groups['ID'] = pd.to_numeric(df_food_groups['ID'], errors='coerce')
df_food_groups = df_food_groups.dropna(subset=['ID'])
df_food_groups['ID'] = df_food_groups['ID'].astype(int)

# Cleaning the energy data
df_energy = df_energy.iloc[3:].reset_index(drop=True)
df_energy.columns = df_energy.iloc[0]  # Set the correct header
df_energy = df_energy[['Nr', 'Energi']] #only keep nr and energi columns
df_energy = df_energy.drop(0)#drop the first row
df_energy.rename(columns={'Nr': 'ID', 'Energi':'Energy'}, inplace=True)
df_energy = df_energy.drop(1)#drop the first row
df_energy.reset_index(drop=True, inplace=True)#Reset the index
df_energy['Energy'] = df_energy['Energy'] / 4.184 # Convert energy intake from KJ to Kcal


# Energy analysis
# Merge df_background and df_energy
df_energy_m = pd.merge(df_energy, df_background, on='ID')

# Map gender numeric values to strings
df_energy_m['Gender'] = df_energy_m['Gender'].map({1: 'Male', 2: 'Female'})

# Calculate mean and standard deviation for each gender
mean_energy_male = df_energy_m[df_energy_m['Gender'] == 'Male']['Energy'].mean()
std_energy_male = df_energy_m[df_energy_m['Gender'] == 'Male']['Energy'].std()
mean_energy_female = df_energy_m[df_energy_m['Gender'] == 'Female']['Energy'].mean()
std_energy_female = df_energy_m[df_energy_m['Gender'] == 'Female']['Energy'].std()


# Plot energy distribution by mean energy intake for each gender
plt.figure(figsize=(10, 6))
sns.histplot(df_energy_m[df_energy_m['Gender'] == 'Male']['Energy'], kde=True, color='blue', label='Male')
sns.histplot(df_energy_m[df_energy_m['Gender'] == 'Female']['Energy'], kde=True, color='pink', label='Female')
plt.axvline(mean_energy_male, color='blue', linestyle='--', label=f'Mean Male: {mean_energy_male:.2f} Kcal')
plt.axvline(mean_energy_male + std_energy_male, color='blue', linestyle=':', label=f'+1 Std Dev Male: {mean_energy_male + std_energy_male:.2f} Kcal')
plt.axvline(mean_energy_male - std_energy_male, color='blue', linestyle=':', label=f'-1 Std Dev Male: {mean_energy_male - std_energy_male:.2f} Kcal')
plt.axvline(mean_energy_female, color='pink', linestyle='--', label=f'Mean Female: {mean_energy_female:.2f} Kcal')
plt.axvline(mean_energy_female + std_energy_female, color='pink', linestyle=':', label=f'+1 Std Dev Female: {mean_energy_female + std_energy_female:.2f} Kcal')
plt.axvline(mean_energy_female - std_energy_female, color='pink', linestyle=':', label=f'-1 Std Dev Female: {mean_energy_female - std_energy_female:.2f} Kcal')
plt.title('Energy intake distribution by Gender')
plt.xlabel('Energy intake (Kcal) per day')
plt.ylabel('Frequency')
plt.legend()
plt.show()

# Create 10-year age groups
df_energy_m['AgeGroup'] = pd.cut(df_energy_m['Age'], bins=range(0, 101, 10), right=False, labels=[f'{i}-{i+9}' for i in range(0, 100, 10)])

# Verify the AgeGroup column
print(df_energy_m[['Age', 'AgeGroup']].head())

# Plot energy intake by age group and gender
plt.figure(figsize=(14, 8))
sns.boxplot(x='AgeGroup', y='Energy', hue='Gender', data=df_energy_m, palette={'Male': 'blue', 'Female': 'pink'})
plt.title('Energy Intake by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Energy intake (Kcal) per day')
plt.legend(title='Gender')
plt.show()

# Food groups analysis

# Classifying the food groups 
# Mapping the food groups to the correct category
# The food groups are classified into 5 categories:
# 1. Fruits and nuts
# 2. Vegetables
# 3. Starchy vegetables
# 4. Grains and cereals
# 5. Dairy and alternatives
# 6. Red meat 
# 7. Poultry  
# 8. Eggs
# 9. Fish
# 10. Legumes

# Mapping the food groups to the correct category
food_group_mapping = {
    'Fruits and nuts': [
        'FRUKTB', 'FRU_F', 'SITRUS', 'EPLEP', 'FRU_AF', 'BER_F', 'FRU_U', 'FRU_K', 'SYLT_K', 'SYLT_F', 'FRU_H', 'FRU_TI', 'FRU_T', 'FETFRU', 'SAFTK', 'JUICE'
    ],
    'Vegetables': [
        'GRSAK', 'GRS_FF', 'GULROT', 'KALROT', 'HOKAL', 'BLKAL', 'BROKK', 'LOKPUR', 'KIKAL', 'AGURK', 'TOMAT', 'PAPRIK', 'GRONT', 'ERT_F', 'GROER', 'SOPP', 'GRS_AF', 'GRS_BL', 'GRS_U', 'GRS_K', 'GRS_H', 'SURKAL', 'GRS_S', 'GRS_AK', 'BELGFR'
    ],
    'Starchy vegetables': [
        'POTET', 'POTE_F', 'POTE_P', 'POMMES'
    ],
    'Grains and cereals': [
        'BROD', 'LOFF', 'LOFF_K', 'LOFF_H', 'LOFF_U', 'KNEIPP', 'KNEI_K', 'KNEI_H',
        'KNEI_U', 'GROVBR', 'GROV_K', 'GROV_H', 'BROD_U', 'BROD_A', 'FLATBR',
        'KJEKS', 'LEFSE', 'KORNPR', 'MELRIS', 'MELKOR', 'RIS', 'PASTA', 
        'FROK_S', 'FROK_U', 'PASTPAI', 'KAKER', 'KAKE_G', 'KAKE_T', 'KAKE_A'
    ],
    'Dairy and alternatives': [
        'MELKYO', 'HMELK', 'LMELK', 'EMELK', 'SMELK', 'MELK-S', 
        'YOGHUR', 'MELK_U', 'MELK_A', 'AMELK', 'MELK_K', 'FLOTIS',
        'FLOROM', 'IS', 'MFL_PR', 'OST', 'OST_HO', 'OST_HF', 'OST_HM', 
        'OST_HU', 'OST_BF', 'OST_BH', 'OST_BU', 'SMARGO', 'MARG', 'MARG_S', 
        'MAR_SB', 'MAR_SM', 'MARG_B', 'MAR_BB', 'MAR_BM', 'MARG_A', 'MAR_AB', 
        'MAR_AM', 'MARG_U', 'MARG_L', 'SMOR', 'SMOR_B', 'SMOR_M', 'SMAR_B', 
        'SMAR_M', 'SMAR_U', 'OLJE_M'
    ],
    'Red meat': [
        'KJOTT', 'KJOT_R', 'SVIN', 'STORFE', 'FAAR', 'VILT', 'ADYR', 
        'KJOT_U', 'KJOT_M', 'KJOT_S', 'KJOT_P', 'POLSE', 'KJO_AF', 
        'KJO_PL', 'KJOTPA', 'LEVERP', 'KJO_AP', 'KJORET', 'BLODIN', 'BLOD', 'LEVER'
    ],
    'Poultry': [
        'KJOT_HV', 'KYLKAL', 'ANDG', 'KYL_G'
    ],
    'Eggs': [
        'EGG'
    ],
    'Fish': [
        'FISK', 'FISK_F', 'LAKSOR', 'SILDMA', 'FIS_FA', 'FIS_MH', 
        'FISK_M', 'FISK_H', 'FISK_S', 'LUTEFI', 'FIS_FV', 'FISK_U', 
        'FISK_P', 'FIS_FP', 'FIS_PF', 'FISKPA', 'SKALIN', 'SKALDY', 'IMAT_F', 'FISRET'
    ],
    'Legumes': [
        'BELGFR'
    ],
    'Condiments and sauces': [
        'IMAT_K', 'MAJORE', 'DRESS', 'MSALAT', 'SAUS', 'PULVER', 'KRYDD'
    ],
    'Sweets and snacks': [
        'SUKSOT', 'SUKHS', 'SUKKER', 'SOTM_A', 'SOT_EF', 'HONSIR', 'SOTPA', 
        'SJOSOT', 'SJOK', 'PASTIL', 'GODTER', 'SNACKS', 'PCHIPS', 'SNAC_A'
    ],
    'Beverages': [
        'DRIKKE', 'KAFFE', 'KAFFE_F', 'KAFFE_I', 'KAFFE_K', 'KAFFE_U', 
        'KAFFE_E', 'TE', 'TE_V', 'TE_G', 'TE_UN', 'TE_U', 'SAFBRU', 'SABR_S', 
        'BRUS_S', 'SAFT_S', 'NEKTAR', 'LDRI_S', 'EDRIK', 'SABR_L', 'BRUS_L', 
        'SAFT_L', 'LDRI_L', 'EDRIK_L', 'SABR_U', 'DRVANN', 'VANN_S', 'VANN_F',
        'OLVBR', 'OL', 'OL_LP', 'OL_EX', 'OL_U', 'VIN', 'BRVIN', 'OLV_AF'
    ],
    'Miscellaneous': [
        'DIVERS', 'NPREP', 'VEGPR', 'DIV_A', 'VANN_I', 'FETT_A'
    ]
}

# Create a reverse mapping from food group codes to categories
reverse_food_group_mapping = {}
for category, codes in food_group_mapping.items():
    for code in codes:
        reverse_food_group_mapping[code] = category

# Reshape the DataFrame to a long format
df_long = df_food_groups.melt(id_vars=['ID', 'TOTALT'], var_name='FoodGroup', value_name='Amount')

# Map the food group codes to categories
df_long['Category'] = df_long['FoodGroup'].map(reverse_food_group_mapping)

# Check for any unmapped food group codes
unmapped_codes = df_long[df_long['Category'].isnull()]['FoodGroup'].unique()
if len(unmapped_codes) > 0:
    print(f"Unmapped food group codes: {unmapped_codes}")

# Calculate the total amount of food consumed per category
df_food = df_long.groupby(['ID', 'Category'])['Amount'].sum().reset_index()
df_food = df_food.pivot(index='ID', columns='Category', values='Amount').reset_index()
df_food = pd.merge(df_background[['ID', 'Age', 'Gender', 'Education', 'Region']], df_food, on='ID') # Merge with background data including Region
df_food['Gender'] = df_food['Gender'].map({1: 'Male', 2: 'Female'}) # Map gender numeric values to strings


# Plotting average consumption of male and female by food categories
# Calculate average consumption by gender
categories = [c for c in df_food.columns if c not in ['ID', 'Age', 'Gender', 'Education', 'AgeGroup', 'Beverages', 'Miscellaneous']]
average_consumption = df_food.groupby('Gender')[categories].mean().T

# Plot average consumption by gender and leave out beverages and miscellaneous categories
average_consumption.plot(kind='bar', figsize=(14, 8), color=['pink', 'blue'])
plt.title('Average Consumption by Food Category and Gender')
plt.xlabel('Food Category')
plt.ylabel('Average Amount Consumed')
plt.legend(title='Gender')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Calculate average consumption by age group
# Create 10-year age groups
df_food['AgeGroup'] = pd.cut(df_food['Age'], bins=range(0, 101, 10), right=False, labels=[f'{i}-{i+9}' for i in range(0, 100, 10)])
average_consumption_age_group = df_food.groupby('AgeGroup')[categories].mean().T

# Define colors for each food group
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
    'Condiments and sauces': '#eaecee',
    'Sweets and snacks': '#808b96',
    'Beverages': '#aab7b8',
    'Miscellaneous': '#34495e'
}
#%%
# Ensure the colors are applied in the correct order
colors = [food_group_colors[category] for category in average_consumption_age_group.index]

# Plot average consumption by age group with age groups on y axis and food categories as stacked bars
average_consumption_age_group.T.plot(kind='barh', stacked=True, figsize=(14, 8), color=colors)
plt.title('Average Consumption by Food Category and Age Group')
plt.xlabel('Average Amount Consumed (g)')
plt.ylabel('Age Group')
plt.legend(title='Food Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

#%%
# Plotting consumption of food categories by education level and food categories
# Calculate average consumption by education level
average_consumption_education = df_food.groupby('Education')[categories].mean().T
# Plot average consumption by education level on y axis and categories as stacked bars
average_consumption_education.T.plot(kind='barh', stacked=True, figsize=(14, 8), color = colors)
plt.title('Average Consumption by Food Category and Education Level')
plt.xlabel('Average Amount Consumed (g)')
plt.ylabel('Education Level')
plt.legend(title='Food Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
#%%
#Redefine categories to be in the correct order 
categories = ['Fruits and nuts', 'Vegetables', 'Starchy vegetables', 'Grains and cereals', 'Legumes','Dairy and alternatives', 'Red meat', 'Poultry', 'Eggs', 'Fish']
# Calculate average consumption by region
average_consumption_region = df_food.groupby('Region')[categories].mean()

# Plot average consumption by region with subplots for each food category
regions = average_consumption_region.index
fig, axes = plt.subplots(nrows=len(regions), ncols=1, figsize=(10, 2 * len(regions)), sharex=True)

for i, region in enumerate(regions):
    average_consumption_region.loc[region].plot(kind='bar', ax=axes[i], color=colors[:len(categories)])
    axes[i].set_title(f'Average Consumption in {region}')
    if i == len(regions) - 1:
        axes[i].set_xlabel('Food Category')
    else:
        axes[i].set_xlabel('')
    axes[i].set_xticks(range(len(categories)))
    axes[i].set_xticklabels(categories, rotation=45, ha='right')
    if i == len(regions) // 2:
        axes[i].set_ylabel('Average Amount Consumed (g)')
    else:
        axes[i].set_ylabel('')

plt.tight_layout(pad=2.0)
plt.show()
# %%
#Export a table with average consumption by gender, age group and food category 
# Export a table with average consumption by gender, age group, and food category
average_consumption_gender_age = df_food.groupby(['Gender', 'AgeGroup'])[categories].mean().reset_index()

# Melt the DataFrame to long format
average_consumption_gender_age_long = average_consumption_gender_age.melt(id_vars=['Gender', 'AgeGroup'], var_name='FoodCategory', value_name='Average amount consumed (g)')

#Fill na to 0  in Average amount consumed
average_consumption_gender_age_long['Average amount consumed (g)'].fillna(0, inplace=True)

# Save the table to a CSV file
output_path = os.path.join('..', 'data', 'auxillary', 'average_consumption_by_gender_age.csv')
average_consumption_gender_age_long.to_csv(output_path, index=False)

print(f"Average consumption by gender and age group has been exported to {output_path}")

#%%
# Import the food composition data from the auxillary folder
food_composition_path = os.path.join('..', 'data', 'auxillary', 'food_composition.xlsx')
df_food_composition = pd.read_excel(food_composition_path)
#Rename the index column to Categories
df_food_composition.rename(columns={'Main Category': 'Categories'}, inplace=True)

# Calculate the percentage of dry matter, fat, protein, and carbohydrates for age, gender and food category
average_consumption_gender_age_long['TotalDryMatter'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['FoodCategory'].map(df_food_composition.set_index('Categories')['Percent Dry Matter']) / 100
)

average_consumption_gender_age_long['TotalFat'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['FoodCategory'].map(df_food_composition.set_index('Categories')['Fat (g)']) / 100
)

average_consumption_gender_age_long['TotalProtein'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['FoodCategory'].map(df_food_composition.set_index('Categories')['Protein (g)']) / 100
)

average_consumption_gender_age_long['TotalCarbohydrates'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['FoodCategory'].map(df_food_composition.set_index('Categories')['Carbohydrate (g)']) / 100
)

# TotalCalories should NOT be divided by 100 because it's already per 100g in the food composition data
average_consumption_gender_age_long['TotalCalories'] = (
    average_consumption_gender_age_long['Average amount consumed (g)'] *
    average_consumption_gender_age_long['FoodCategory'].map(df_food_composition.set_index('Categories')['Kilokalorier (kcal)'])/100
)

# Group by Gender, AgeGroup, and FoodCategory to calculate the total amount of each nutrient
df_nutrient_totals = average_consumption_gender_age_long.groupby(['Gender', 'AgeGroup', 'FoodCategory']).agg({
    'TotalDryMatter': 'sum',
    'TotalFat': 'sum',
    'TotalProtein': 'sum',
    'TotalCarbohydrates': 'sum',
    'TotalCalories': 'sum'
}).reset_index()

# Drop rows where TotalCalories is 0
df_nutrient_totals = df_nutrient_totals[df_nutrient_totals['TotalCalories'] > 0].reset_index(drop=True)


# %%
# examine the data in df_nutrient_totals
print(df_nutrient_totals.head())

#Check the total calories by age 
total_calories_age = df_nutrient_totals.groupby('AgeGroup')[['TotalCalories', 'TotalFat','TotalCarbohydrates']].sum()
total_calories_age

#%%
# Function to plot population pyramid for a given nutrient metric
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd

# Function to plot population pyramid for a given nutrient metric
def plot_population_pyramid(metric, ylabel, color_dict):
    age_groups = df_nutrient_totals['AgeGroup'].unique()
    age_groups = sorted(age_groups)  # Ensure age groups are sorted

    # Pivot the data for population pyramid format
    pivot_data = df_nutrient_totals.pivot_table(index=['AgeGroup', 'Gender'], columns='FoodCategory', values=metric, aggfunc='sum', fill_value=0)

    # Increase the figure size to make the plot wider
    fig, ax = plt.subplots(figsize=(14, 8))  # Adjust width for better visualization

    # Loop through the age groups and stack the food categories
    for age_group in age_groups:
        # Retrieve male and female data for the current age group
        male_data = pivot_data.loc[(age_group, 'Male')] if (age_group, 'Male') in pivot_data.index else pd.Series(0, index=pivot_data.columns)
        female_data = pivot_data.loc[(age_group, 'Female')] if (age_group, 'Female') in pivot_data.index else pd.Series(0, index=pivot_data.columns)

        # Initialize cumulative values for stacked bars
        female_cum_values = pd.Series(0, index=pivot_data.columns)
        male_cum_values = pd.Series(0, index=pivot_data.columns)

        # Plot female data on the left (negative side)
        for food_category in pivot_data.columns:
            ax.barh(age_group, -female_data[food_category], left=-female_cum_values[food_category], 
                    color=color_dict.get(food_category, '#333333'), edgecolor='none')
            female_cum_values += female_data[food_category]

        # Plot male data on the right (positive side)
        for food_category in pivot_data.columns:
            ax.barh(age_group, male_data[food_category], left=male_cum_values[food_category], 
                    color=color_dict.get(food_category, '#333333'), edgecolor='none')
            male_cum_values += male_data[food_category]

    # Set axis labels and title
    ax.set_xlabel(ylabel)
    ax.set_ylabel('Age Group')
    ax.set_title(f'{ylabel} by Age Group and Gender')

    # Add labels for "Male" and "Female"
    ax.text(0.95, 1.02, 'Male', transform=ax.transAxes, fontsize=12, verticalalignment='center', horizontalalignment='center', color='blue')
    ax.text(0.05, 1.02, 'Female', transform=ax.transAxes, fontsize=12, verticalalignment='center', horizontalalignment='center', color='red')

    # Add color-coded legend outside the plot to avoid overlap
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_dict[key]) for key in color_dict.keys()]
    ax.legend(handles, color_dict.keys(), title='Food Groups', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Tighten the layout and adjust spacing between bars
    plt.subplots_adjust(left=0.1, right=0.8, top=0.9, bottom=0.1)  # Adjust margins
    plt.tight_layout()
    plt.show()

# Example usage: Plotting for TotalCalories, TotalProtein, TotalFat, and TotalCarbohydrates
plot_population_pyramid('TotalCalories', 'Total Calories (kcal)', food_group_colors)
plot_population_pyramid('TotalProtein', 'Total Protein (g)', food_group_colors)
plot_population_pyramid('TotalFat', 'Total Fat (g)', food_group_colors)
plot_population_pyramid('TotalCarbohydrates', 'Total Carbohydrates (g)', food_group_colors)

