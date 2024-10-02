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
consumption_df['Carbon_Intake'] = consumption_df[
    [f'{nutrient}_Carbon' for nutrient in carbon_content]
].sum(axis=1)

# Convert Phosphorus intake from mg to grams
consumption_df['Phosphorus_Intake'] = consumption_df['Phosphorus'] / 1000  # Convert mg to grams if necessary

# Step 5: Calculate Age Category
def get_age_category(age_group):
    age = int(age_group.split('-')[0])
    if 10 <= age <= 19:
        return 'Adolescent'
    elif 20 <= age <= 59:
        return 'Adult'
    else:
        return 'OlderAdult'

consumption_df['AgeCategory'] = consumption_df['AgeGroup'].apply(get_age_category)

# Step 6: Calculate Excretion Rates Based on Age Category
def get_excretion_rates(age_category):
    if age_category == 'Adolescent':
        fecal_rate = 0.04   # 4%
        urinary_rate = 0.008  # 0.8%
    elif age_category == 'Adult':
        fecal_rate = 0.05   # 5%
        urinary_rate = 0.01  # 1%
    else:
        fecal_rate = 0.06   # 6%
        urinary_rate = 0.012  # 1.2%
    return fecal_rate, urinary_rate

# Apply excretion rates to each row
consumption_df['Carbon_Feces'] = consumption_df.apply(
    lambda row: row['Carbon_Intake'] * get_excretion_rates(row['AgeCategory'])[0], axis=1
)
consumption_df['Carbon_Urine'] = consumption_df.apply(
    lambda row: row['Carbon_Intake'] * get_excretion_rates(row['AgeCategory'])[1], axis=1
)

# Step 7: Calculate Methane Emission
def get_methane_emission(age_category, energy_intake):
    # Base methane emission per age category (grams/day)
    if age_category == 'Adolescent':
        base_methane_emission = 0.5
    elif age_category == 'Adult':
        base_methane_emission = 0.6
    else:
        base_methane_emission = 0.7
    methane_emission = base_methane_emission * (energy_intake / 2000)  # Scale by energy intake
    carbon_from_ch4 = methane_emission * (12/16)  # Convert CH₄ to Carbon
    return carbon_from_ch4

# Calculate total energy intake per person per day for each group
total_energy = consumption_df.groupby(['Gender', 'AgeGroup'])['Calories'].transform('sum')
consumption_df['TotalCalories'] = total_energy

# Calculate methane emission per person
average_energy_intake = consumption_df.groupby(['Gender', 'AgeGroup'])['Calories'].transform('mean')
consumption_df['AverageEnergyIntake'] = average_energy_intake
consumption_df['Carbon_CH4_Total'] = consumption_df.apply(
    lambda row: get_methane_emission(row['AgeCategory'], row['AverageEnergyIntake']), axis=1
)

# Distribute methane emission proportionally to each food item's caloric contribution
consumption_df['Carbon_CH4'] = consumption_df['Carbon_CH4_Total'] * (consumption_df['Calories'] / consumption_df['TotalCalories'])

# Step 8: Calculate Net Carbon Retention per Food Item
# First, calculate total Carbon Intake per person per day for each group
total_carbon_intake = consumption_df.groupby(['Gender', 'AgeGroup'])['Carbon_Intake'].transform('sum')
consumption_df['TotalCarbon_Intake'] = total_carbon_intake

# Now, retrieve NetCarbonRetention from intake_df
# Assuming intake_df is already calculated and available
# Merge NetCarbonRetention into consumption_df
consumption_df = consumption_df.merge(
    intake_df[['Gender', 'AgeGroup', 'NetCarbonRetention']],
    on=['Gender', 'AgeGroup'],
    how='left'
)

# Distribute NetCarbonRetention proportionally to each food item's Carbon contribution
consumption_df['NetCarbonRetention_Item'] = consumption_df['NetCarbonRetention'] * (consumption_df['Carbon_Intake'] / consumption_df['TotalCarbon_Intake'])

# Step 9: Calculate Carbon CO₂ Output per Food Item
consumption_df['Carbon_CO2'] = consumption_df['Carbon_Intake'] - (
    consumption_df['Carbon_Feces'] + consumption_df['Carbon_Urine'] + consumption_df['Carbon_CH4'] + consumption_df['NetCarbonRetention_Item']
)

# Step 10: Calculate Phosphorus Excretion
# Phosphorus excretion rates
phosphorus_urine_rate = 0.67
phosphorus_feces_rate = 0.33

consumption_df['Phosphorus_Urine'] = consumption_df['Phosphorus_Intake'] * phosphorus_urine_rate
consumption_df['Phosphorus_Feces'] = consumption_df['Phosphorus_Intake'] * phosphorus_feces_rate

# Step 11: Select Columns for Export
export_columns = [
    'Gender', 'AgeGroup', 'FoodCategory', 'DryMatter', 'Fat', 'Protein', 'Carbohydrates', 'Calories','NetCarbonRetention',
    'Carbon_Intake', 'Carbon_Feces', 'Carbon_Urine', 'Carbon_CO2', 'Carbon_CH4',
    'Phosphorus_Intake', 'Phosphorus_Feces', 'Phosphorus_Urine'
]

export_df = consumption_df[export_columns]
export_df.head()

#exporting the data to auxillary folder
output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary', 'human_balance.xlsx')
export_df.to_excel(output_path, index=False)
print(f"Data exported to {output_path}")

#%%
#plots for the data
# Ensure that 'AgeGroup' is ordered correctly
age_group_order = ['10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79']
intake_df['AgeGroup'] = pd.Categorical(intake_df['AgeGroup'], categories=age_group_order, ordered=True)

# Set the style for all plots
sns.set_style('whitegrid')

#%%

# Plot Yearly Carbon Retention
plt.figure(figsize=(12, 6))
sns.barplot(data=intake_df, x='AgeGroup', y='YearlyCarbonRetention_kg', hue='Gender', palette='Set3')
plt.title('Yearly Net Carbon Retention by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Yearly Net Carbon Retention (kg/year)')
plt.legend(title='Gender')
plt.tight_layout()
plt.show()

# Plot Yearly Phosphorus Retention
plt.figure(figsize=(12, 6))
sns.barplot(data=intake_df, x='AgeGroup', y='YearlyPhosphorusRetention_kg', hue='Gender', palette='Set1')
plt.title('Yearly Net Phosphorus Retention by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Yearly Net Phosphorus Retention (kg/year)')
plt.legend(title='Gender')
plt.tight_layout()
plt.show()

# Melt the DataFrame for Carbon Outputs
carbon_outputs = intake_df.melt(
    id_vars=['Gender', 'AgeGroup'],
    value_vars=['Carbon_CO2_Output', 'Carbon_CH4_Output', 'Carbon_Feces_Output', 'Carbon_Urine_Output'],
    var_name='Output_Type',
    value_name='Carbon_Output'
)

# Ensure 'Output_Type' has meaningful labels
carbon_outputs['Output_Type'] = carbon_outputs['Output_Type'].replace({
    'Carbon_CO2_Output': 'CO₂ Output',
    'Carbon_CH4_Output': 'CH₄ Output',
    'Carbon_Feces_Output': 'Fecal Output',
    'Carbon_Urine_Output': 'Urinary Output'
})

# Plot Daily Carbon Outputs by Age Group
plt.figure(figsize=(12, 6))
sns.barplot(
    data=carbon_outputs,
    x='AgeGroup',
    y='Carbon_Output',
    hue='Output_Type',
    palette='Set1'
)
plt.title('Daily Carbon Outputs by Age Group')
plt.xlabel('Age Group')
plt.ylabel('Carbon Output (g/day)')
plt.legend(title='Output Type')
plt.tight_layout()
plt.show()

# Plot Daily Net Carbon Retention by Age Group and Gender
plt.figure(figsize=(12, 6))
sns.lineplot(data=intake_df, x='AgeGroup', y='NetCarbonRetention', hue='Gender', marker='o', palette='Set2')
plt.title('Daily Net Carbon Retention by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Net Carbon Retention (g/day)')
plt.legend(title='Gender')
plt.tight_layout()
plt.show()


# Plot Average Daily Carbon Intake by Age Group and Gender
plt.figure(figsize=(12, 6))
sns.barplot(
    data=intake_df,
    x='AgeGroup',
    y='TotalCarbonIntake',
    hue='Gender',
    palette='Set1'
)
plt.title('Average Daily Carbon Intake by Age Group and Gender')
plt.xlabel('Age Group')
plt.ylabel('Total Carbon Intake (g/day)')
plt.legend(title='Gender')
plt.tight_layout()
plt.show()
