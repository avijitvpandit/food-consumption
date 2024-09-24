
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

df_background = df_background.iloc[:, :-3] #drop the last three columns
df_background.rename(columns={'Nr': 'ID'}, inplace=True) #rename Nr to ID


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
df_energy.rename(columns={'Nr': 'ID'}, inplace=True)
df_energy = df_energy.drop(1)#drop the first row
df_energy.reset_index(drop=True, inplace=True)#Reset the index

#%%
# Analysis of energy 
# Merge the 