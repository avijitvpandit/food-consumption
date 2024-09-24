
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
plt.title('Energy distribution by Gender')
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