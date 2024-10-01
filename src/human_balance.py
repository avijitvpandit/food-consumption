#%%
#import the relevant libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

#%%
# Load the Excel file
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary', 'Average consumption by age and gender.xlsx')
consumption_df = pd.read_excel(file_path)

#%%
# Step 2: Rename Columns for Clarity
consumption_df.rename(columns={
    'TotalCarbohydrates': 'Carbohydrates', 
    'TotalProtein': 'Protein', 
    'TotalFat': 'Fat',
    'TotalDryMatter': 'DryMatter',
    'TotalPhosphorus': 'Phosphorus',
    'TotalCalories': 'Calories'  # Ensure the calories column is correctly named
}, inplace=True)

# Step 3: Define Carbon Content in Macronutrients
carbon_content = {
    'Carbohydrates': 0.44,  # 44% Carbon
    'Protein': 0.53,        # 53% Carbon
    'Fat': 0.77             # 77% Carbon
}

# Step 4: Calculate Carbon Intake from Macronutrients
for nutrient, carbon_fraction in carbon_content.items():
    consumption_df[f'{nutrient}_Carbon'] = consumption_df[nutrient] * carbon_fraction

# Total Carbon Intake per food item
consumption_df['TotalCarbonIntake'] = consumption_df[
    [f'{nutrient}_Carbon' for nutrient in carbon_content]
].sum(axis=1)

# Convert Phosphorus intake from mg to grams if necessary
consumption_df['TotalPhosphorusIntake'] = consumption_df['Phosphorus'] / 1000  # Adjust if already in grams

# Step 5: Aggregate Intake by Gender and AgeGroup
intake_df = consumption_df.groupby(['Gender', 'AgeGroup']).agg({
    'TotalCarbonIntake': 'sum',
    'TotalPhosphorusIntake': 'sum',
    'AverageEnergyIntake': 'mean'
}).reset_index()

# Function to determine age group category
def get_age_category(age_group):
    age = int(age_group.split('-')[0])
    if age >= 10 and age <= 19:
        return 'Adolescent'
    elif age >= 20 and age <= 59:
        return 'Adult'
    else:
        return 'OlderAdult'

# Apply age category
intake_df['AgeCategory'] = intake_df['AgeGroup'].apply(get_age_category)

# Adjusted Carbon Retention Calculations
def calculate_growth_carbon_retention(row):
    # Set variables for growth or loss
    if row['AgeCategory'] == 'Adolescent':
        if row['Gender'] == 'Female':
            average_weight_gain_per_year = 7  # kg/year
        else:  # Male
            average_weight_gain_per_year = 9  # kg/year
        daily_weight_change = average_weight_gain_per_year * 1000 / 365  # grams/day
    elif row['AgeCategory'] == 'OlderAdult':
        average_weight_loss_per_year = 2  # kg/year
        daily_weight_change = -average_weight_loss_per_year * 1000 / 365  # grams/day (negative for loss)
    else:
        daily_weight_change = 0  # No weight change for adults

    # Lean and fat mass fractions
    lean_mass_fraction = 0.7
    fat_mass_fraction = 0.3
    # Carbon content
    carbon_in_lean_mass = 0.18
    carbon_in_fat_mass = 0.76
    # Calculate Carbon retention or loss
    carbon_retained = (
        daily_weight_change * lean_mass_fraction * carbon_in_lean_mass +
        daily_weight_change * fat_mass_fraction * carbon_in_fat_mass
    )
    return carbon_retained

intake_df['Growth_Carbon_Retention'] = intake_df.apply(calculate_growth_carbon_retention, axis=1)

# Calculate Net Carbon Retention
intake_df['NetCarbonRetention'] = intake_df['Growth_Carbon_Retention']

# Adjust Excretion Rates
def get_excretion_rates(age_category):
    if age_category == 'Adolescent':
        fecal_rate = 0.04  # 4%
        urinary_rate = 0.008  # 0.8%
    elif age_category == 'Adult':
        fecal_rate = 0.05  # 5%
        urinary_rate = 0.01  # 1%
    else:  # OlderAdult
        fecal_rate = 0.06  # 6%
        urinary_rate = 0.012  # 1.2%
    return fecal_rate, urinary_rate

def estimate_fecal_urinary_carbon(row):
    fecal_rate, urinary_rate = get_excretion_rates(row['AgeCategory'])
    fecal_carbon = row['TotalCarbonIntake'] * fecal_rate
    urinary_carbon = row['TotalCarbonIntake'] * urinary_rate
    return fecal_carbon, urinary_carbon

fecal_urinary_carbon = intake_df.apply(estimate_fecal_urinary_carbon, axis=1)
intake_df['Carbon_Feces_Output'] = [x[0] for x in fecal_urinary_carbon]
intake_df['Carbon_Urine_Output'] = [x[1] for x in fecal_urinary_carbon]

# Adjust Methane Emissions
def get_methane_emission(age_category, energy_intake):
    # Base methane emission per age category
    if age_category == 'Adolescent':
        base_methane_emission = 0.5  # grams/day of CH₄
    elif age_category == 'Adult':
        base_methane_emission = 0.6
    else:  # OlderAdult
        base_methane_emission = 0.7
    # Adjust for energy intake relative to 2000 kcal/day
    methane_emission = base_methane_emission * (energy_intake / 2000)
    # Carbon content in methane (CH₄)
    carbon_from_ch4 = methane_emission * (12/16)
    return carbon_from_ch4

intake_df['Carbon_CH4_Output'] = intake_df.apply(
    lambda row: get_methane_emission(row['AgeCategory'], row['AverageEnergyIntake']), axis=1)

# Calculate Carbon_CO2_Output Based on Mass Balance
def estimate_carbon_co2_output(row):
    carbon_co2_output = (
        row['TotalCarbonIntake'] -
        row['Carbon_Feces_Output'] -
        row['Carbon_Urine_Output'] -
        row['Carbon_CH4_Output'] -
        row['NetCarbonRetention']
    )
    return carbon_co2_output

intake_df['Carbon_CO2_Output'] = intake_df.apply(estimate_carbon_co2_output, axis=1)

# Total Carbon Output
intake_df['TotalCarbonOutput'] = (
    intake_df['Carbon_CO2_Output'] +
    intake_df['Carbon_CH4_Output'] +
    intake_df['Carbon_Feces_Output'] +
    intake_df['Carbon_Urine_Output']
)

# Verify Mass Balance
intake_df['Check_TotalCarbon'] = intake_df['TotalCarbonIntake'] - intake_df['TotalCarbonOutput'] + intake_df['NetCarbonRetention']

# Adjust Phosphorus Retention
def calculate_phosphorus_growth_retention(row):
    lean_mass_fraction = 0.7
    fat_mass_fraction = 0.3
    phosphorus_in_lean_mass = 0.01  # 1% Phosphorus in lean mass
    carbon_in_lean_mass = 0.18
    carbon_in_fat_mass = 0.76
    if row['AgeCategory'] == 'Adolescent' or row['AgeCategory'] == 'OlderAdult':
        # Reverse calculation to get daily weight change
        daily_weight_change = row['Growth_Carbon_Retention'] / (
            lean_mass_fraction * carbon_in_lean_mass + fat_mass_fraction * carbon_in_fat_mass
        )
        phosphorus_retained = daily_weight_change * lean_mass_fraction * phosphorus_in_lean_mass
        return phosphorus_retained
    else:
        return 0

intake_df['Growth_Phosphorus_Retention'] = intake_df.apply(calculate_phosphorus_growth_retention, axis=1)

# Calculate Net Phosphorus Retention
def calculate_net_phosphorus_retention(row):
    net_phosphorus_retention = row['Growth_Phosphorus_Retention']
    return net_phosphorus_retention

intake_df['NetPhosphorusRetention'] = intake_df.apply(calculate_net_phosphorus_retention, axis=1)

# Adjust Phosphorus Outputs
intake_df['Phosphorus_Urine_Output'] = intake_df['TotalPhosphorusIntake'] * 0.67
intake_df['Phosphorus_Feces_Output'] = intake_df['TotalPhosphorusIntake'] * 0.33

# Total Phosphorus Output
intake_df['TotalPhosphorusOutput'] = (
    intake_df['Phosphorus_Urine_Output'] +
    intake_df['Phosphorus_Feces_Output']
)

# Verify Phosphorus Mass Balance
intake_df['Check_TotalPhosphorus'] = intake_df['TotalPhosphorusIntake'] - intake_df['TotalPhosphorusOutput'] + intake_df['NetPhosphorusRetention']

# **Calculate Yearly Balances**
intake_df['YearlyCarbonRetention'] = intake_df['NetCarbonRetention'] * 365  # grams/year
intake_df['YearlyPhosphorusRetention'] = intake_df['NetPhosphorusRetention'] * 365  # grams/year

# Convert grams to kilograms for yearly retention
intake_df['YearlyCarbonRetention_kg'] = intake_df['YearlyCarbonRetention'] / 1000
intake_df['YearlyPhosphorusRetention_kg'] = intake_df['YearlyPhosphorusRetention'] / 1000

# Display Results
output_columns = [
    'Gender', 'AgeGroup', 'AverageEnergyIntake', 'TotalCarbonIntake', 'Carbon_CO2_Output',
    'Carbon_CH4_Output', 'Carbon_Feces_Output', 'Carbon_Urine_Output',
    'NetCarbonRetention', 'YearlyCarbonRetention_kg',
    'TotalPhosphorusIntake', 'Phosphorus_Urine_Output', 'Phosphorus_Feces_Output',
    'NetPhosphorusRetention', 'YearlyPhosphorusRetention_kg'
]

print(intake_df[output_columns])
#%%
# Plot Yearly Carbon Retention
plt.figure(figsize=(12, 6))
sns.barplot(data=intake_df, x='AgeGroup', y='YearlyCarbonRetention_kg', hue='Gender')
plt.title('Yearly Net Carbon Retention by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Yearly Net Carbon Retention (kg/year)')
plt.legend(title='Gender')
plt.show()

plt.figure(figsize=(12, 6))
sns.barplot(data=intake_df, x='AgeGroup', y='YearlyPhosphorusRetention_kg', hue='Gender')
plt.title('Yearly Net Phosphorus Retention by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Yearly Net Phosphorus Retention (kg/year)')
plt.legend(title='Gender')
plt.show()

carbon_outputs = intake_df.melt(
    id_vars=['Gender', 'AgeGroup'],
    value_vars=['Carbon_CO2_Output', 'Carbon_CH4_Output', 'Carbon_Feces_Output', 'Carbon_Urine_Output'],
    var_name='Output_Type',
    value_name='Carbon_Output'
)

# Plot Carbon Outputs
plt.figure(figsize=(12, 6))
sns.barplot(
    data=carbon_outputs,
    x='AgeGroup',
    y='Carbon_Output',
    hue='Output_Type'
)
plt.title('Daily Carbon Outputs by Age Group')
plt.xlabel('Age Group')
plt.ylabel('Carbon Output (g/day)')
plt.legend(title='Output Type')
plt.show()

plt.figure(figsize=(12, 6))
sns.lineplot(data=intake_df, x='AgeGroup', y='NetCarbonRetention', hue='Gender', marker='o')
plt.title('Daily Net Carbon Retention by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Net Carbon Retention (g/day)')
plt.legend(title='Gender')
plt.show()
#%%
sns.set_style('whitegrid')

# Create the bar plot
plt.figure(figsize=(12, 6))
sns.barplot(
    data=intake_df,
    x='AgeGroup',
    y='TotalCarbonIntake',
    hue='Gender',
    palette='Set1'
)

# Add titles and labels
plt.title('Average Daily Carbon Intake by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Total Carbon Intake (g/day)')
plt.legend(title='Gender')

# Show the plot
plt.tight_layout()
plt.show()
# %%
