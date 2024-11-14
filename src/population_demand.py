#%% Neccessary Libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

#%% importing population data
#importing population data
file_path = os.path.join('..', 'data', 'raw', 'ssb', 'Population - age and gender.xlsx')
df_pop = pd.read_excel(file_path, skiprows=3, skipfooter=3)
df_pop.rename(columns={'Unnamed: 0': 'Gender', 'Unnamed: 1': 'AgeGroup'}, inplace=True)
df_pop.dropna(inplace=True)
#grouping 70+ as one age group
df_pop['AgeGroup'] = df_pop['AgeGroup'].replace([
    '70-79 years', '80-89 years', '90-99 years', '100 years or older'
], '70 years or older')

# Grouping the rest as 70 years or older
df_pop = df_pop.groupby(['Gender', 'AgeGroup']).sum().reset_index()

# %%
# Creating a population pyramid
def plot_population_pyramid(df, age_group_col, gender_col, population_col, year_col):
    # Melting the dataframe to have years as a column
    df_melted = df.melt(id_vars=[gender_col, age_group_col], var_name=year_col, value_name=population_col)
    
    years = df_melted[year_col].unique()
    for year in years:
        df_year = df_melted[df_melted[year_col] == year]
        df_pivot = df_year.pivot(index=age_group_col, columns=gender_col, values=population_col)
        df_pivot = df_pivot.fillna(0)
        
        # Plotting
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plotting males
        ax.barh(df_pivot.index, -df_pivot['Males'], color='blue', label='Male')
        
        # Plotting females
        ax.barh(df_pivot.index, df_pivot['Females'], color='pink', label='Female')
        
        ax.set_xlabel('Population')
        ax.set_ylabel('Age Group')
        ax.set_title(f'Population Pyramid for {year}')
        ax.legend()
        
        # Format x-axis labels to show absolute values
        ax.set_xticklabels([str(abs(int(x))) for x in ax.get_xticks()])
        
        plt.tight_layout()
        plt.show()

# Calling the function with the prepared data
plot_population_pyramid(df_pop, 'AgeGroup', 'Gender', 'value', 'variable')

# %%
# Read the NK2 and NK3 data from auxiliary
folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary'))
file_path_nk2 = os.path.join(folder_path, 'average percapita consumption_nk2.xlsx')
file_path_nk3 = os.path.join(folder_path, 'average percapita consumption_nk3.xlsx')

df_nk2 = pd.read_excel(file_path_nk2)
df_nk3 = pd.read_excel(file_path_nk3)
age_group_mapping = {
    '0-9': '0-9 years',
    '10-19': '10-19 years',
    '20-29': '20-29 years',
    '30-39': '30-39 years',
    '40-49': '40-49 years',
    '50-59': '50-59 years',
    '60-69': '60-69 years',
    '70+': '70 years or older'
}

df_nk2['AgeGroup'] = df_nk2['AgeGroup'].map(age_group_mapping)
df_nk3['AgeGroup'] = df_nk3['AgeGroup'].map(age_group_mapping)
df_nk2.dropna(subset=['AgeGroup'], inplace=True)
df_nk3.dropna(subset=['AgeGroup'], inplace=True)

# Standardize gender labels in df_pop, df_nk2, and df_nk3
df_pop['Gender'] = df_pop['Gender'].replace({'male': 'Males', 'female': 'Females'})
df_nk2['Gender'] = df_nk2['Gender'].replace({'male': 'Males', 'female': 'Females'})
df_nk3['Gender'] = df_nk3['Gender'].replace({'male': 'Males', 'female': 'Females'})

# Calculate consumption for each gender
df_pop_nk2 = pd.DataFrame()
df_pop_nk3 = pd.DataFrame()

for gender in ['Males', 'Females']:
    pop_gender = df_pop[df_pop['Gender'] == gender][['AgeGroup', 'Population', 'Gender']]

    # For NK2
    merged_nk2 = pop_gender.merge(df_nk2, on=['AgeGroup', 'Gender'])
    food_columns_nk2 = df_nk2.columns.drop(['AgeGroup', 'Gender'])
    for col in food_columns_nk2:
        merged_nk2[col] = merged_nk2[col] * merged_nk2['Population']
    df_pop_nk2 = pd.concat([df_pop_nk2, merged_nk2], ignore_index=True)

    # For NK3
    merged_nk3 = pop_gender.merge(df_nk3, on=['AgeGroup', 'Gender'])
    food_columns_nk3 = df_nk3.columns.drop(['AgeGroup', 'Gender'])
    for col in food_columns_nk3:
        merged_nk3[col] = merged_nk3[col] * merged_nk3['Population']
    df_pop_nk3 = pd.concat([df_pop_nk3, merged_nk3], ignore_index=True)

# Define color dictionary for food categories
color_dict = {
    'Fruits and nuts': '#FFA500',      # Orange
    'Vegetables': '#90EE90',           # Light green
    'Starchy vegetables': '#8B4513',   # Saddle brown
    'Grains and cereals': '#F4A460',   # Sandy brown
    'Legumes': '#556B2F',              # Dark olive green
    'Dairy and alternatives': '#87CEEB', # Sky blue
    'Eggs': '#FFE4B5',                 # Moccasin
    'Poultry': '#DEB887',              # Burlywood
    'Red meat': '#CD5C5C',             # Indian red
    'Fish': '#4682B4',                 # Steel blue
    'Fats and oils': '#FFD700',        # Gold
    'Sweets and snacks': '#FF69B4',    # Hot pink
    'Miscellaneous': '#808080'         # Grey
}

# Define the plotting function
def plot_population_pyramid(metric, ylabel, color_dict, NorkostVersion):
    # Define the categories in the desired order
    desired_order = [
        'Fruits and nuts',
        'Vegetables',
        'Starchy vegetables',
        'Grains and cereals',
        'Legumes',
        'Dairy and alternatives',
        'Eggs',
        'Poultry',
        'Red meat',
        'Fish',
        'Fats and oils',
        'Sweets and snacks',
        'Miscellaneous'
    ]

    # Use the appropriate dataset based on NorkostVersion
    if NorkostVersion == 'Norkost 2':
        df = df_pop_nk2
    elif NorkostVersion == 'Norkost 3':
        df = df_pop_nk3
    else:
        print("Invalid NorkostVersion. Please specify 'Norkost 2' or 'Norkost 3'.")
        return

    # Sum over AgeGroup and Gender for each category
    pivot_data = df.groupby(['AgeGroup', 'Gender'])[desired_order].sum().reset_index()
    pivot_data = pivot_data.set_index(['AgeGroup', 'Gender']).fillna(0)

    # Plot setup
    fig, ax = plt.subplots(figsize=(14, 10))
    
    age_groups = sorted(df['AgeGroup'].unique())
    
    for age_group in age_groups:
        for gender in ['Males', 'Females']:
            if (age_group, gender) in pivot_data.index:
                data = pivot_data.loc[(age_group, gender)]
            else:
                data = pd.Series(0, index=desired_order)

            cumulative = 0
            for category in desired_order:
                value = data[category]
                color = color_dict.get(category, '#333333')

                if gender == 'Males':
                    ax.barh(age_group, value, left=cumulative, color=color, edgecolor='none')
                    cumulative += value
                else:
                    ax.barh(age_group, -value, left=-cumulative, color=color, edgecolor='none')
                    cumulative += value

    # Formatting
    ax.set_xlabel(ylabel)
    ax.set_ylabel('Age Group')
    ax.set_title(f'{ylabel} by Age Group and Gender ({NorkostVersion})')

    handles = [plt.Rectangle((0,0), 1, 1, color=color_dict.get(cat, '#333333')) for cat in desired_order]
    ax.legend(handles, desired_order, title='Food Categories', bbox_to_anchor=(1.05, 1), loc='upper left')

    max_value = pivot_data[desired_order].sum(axis=1).max()
    ax.set_xlim(-max_value*1.05, max_value*1.05)
    
    ax.text(max_value*0.8, age_groups[-1], 'Males', ha='center', va='bottom', fontsize=12, color='blue')
    ax.text(-max_value*0.8, age_groups[-1], 'Females', ha='center', va='bottom', fontsize=12, color='red')
    ax.axvline(0, color='black', linewidth=0.5)

    plt.tight_layout()
    plt.show()

#%% Plotting the population pyramid for Energy Intake
plot_population_pyramid(
    metric='Energy Intake',
    ylabel='Energy Intake (kcal)',
    color_dict=color_dict,
    NorkostVersion='Norkost 2'  # or 'Norkost 3'
)
