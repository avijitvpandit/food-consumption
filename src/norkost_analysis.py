
#%%importing the libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os


#%%
# Load and clean the data
path = os.path.join('..', 'raw', 'norkost')
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
df_background.rename(columns={"Alder": "Age", "Utdann1": "Education", "Kjønn":"Gender"}, inplace=True)  # rename columns
df_background['Education'] = df_background['Education'].map({
    1: "Primary school",
    2: "Lower secondary school",
    3: "Upper secondary school",
    4: "Post-secondary non-tertiary",
    5: "Short-cycle tertiary",
    6: "Bachelor's or equivalent",
    7: "Master's or equivalent",
    8: "Doctoral or equivalent"
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

#%%
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

#%%
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
df_food = pd.merge(df_background, df_food, on='ID') # Merge with background data
df_food['Gender'] = df_food['Gender'].map({1: 'Male', 2: 'Female'}) # Map gender numeric values to strings

#%%
# Plotting average consumption of male and female by food categories
# Calculate average consumption by gender
categories = [c for c in categories if c not in ['Beverages', 'Miscellaneous']]
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

# Plotting consumption of food categories by 10 year age group

#%%
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

# Ensure the colors are applied in the correct order
colors = [food_group_colors[category] for category in average_consumption_age_group.index]

# Plot average consumption by age group with age groups on y axis and food categories as stacked bars
average_consumption_age_group.T.plot(kind='barh', stacked=True, figsize=(14, 8), color=colors)
plt.title('Average Consumption by Food Category and Age Group')
plt.xlabel('Average Amount Consumed')
plt.ylabel('Age Group')
plt.legend(title='Food Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

#%%
# Plotting consumption of food categories by education level
# Calculate average consumption by education level
# De                   