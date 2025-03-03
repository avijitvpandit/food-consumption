import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_energy_distribution(df_energy_m, mean_energy_male, std_energy_male, mean_energy_female, std_energy_female):
    plt.figure(figsize=(10, 6))
    sns.histplot(df_energy_m[df_energy_m['Gender'] == 'Male']['Energy'], kde=True, color='blue', label='Male')
    sns.histplot(df_energy_m[df_energy_m['Gender'] == 'Female']['Energy'], kde=True, color='pink', label='Female')
    plt.axvline(mean_energy_male, color='blue', linestyle='--', label=f'Mean Male: {mean_energy_male:.2f} Kcal')
    plt.axvline(mean_energy_male + std_energy_male, color='blue', linestyle=':', label=f'+1 Std Dev Male: {mean_energy_male + std_energy_male:.2f} Kcal')
    plt.axvline(mean_energy_male - std_energy_male, color='blue', linestyle=':', label=f'-1 Std Dev Male: {mean_energy_male - std_energy_male:.2f} Kcal')
    plt.axvline(mean_energy_female, color='pink', linestyle='--', label=f'Mean Female: {mean_energy_female:.2f} Kcal')
    plt.axvline(mean_energy_female + std_energy_female, color='pink', linestyle=':', label=f'+1 Std Dev Female: {mean_energy_female + std_energy_female:.2f} Kcal')
    plt.axvline(mean_energy_female - std_energy_female, color='pink', linestyle=':', label=f'-1 Std Dev Female: {mean_energy_female - std_energy_female:.2f} Kcal')
    plt.title('Energy Intake Distribution by Gender')
    plt.xlabel('Energy Intake (Kcal) per day')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_energy_by_age_group(df_energy_m):
    plt.figure(figsize=(14, 8))
    sns.boxplot(
        x='AgeGroup',
        y='Energy',
        hue='Gender',
        data=df_energy_m,
        palette={'Male': 'blue', 'Female': 'pink'}
    )
    plt.title('Energy Intake by Age Group and Gender')
    plt.xlabel('Age Group')
    plt.ylabel('Energy Intake (Kcal) per day')
    plt.legend(title='Gender')
    plt.tight_layout()
    plt.show()

def plot_average_consumption_by_gender(average_consumption):
    average_consumption.plot(kind='bar', figsize=(14, 8), color=['pink', 'blue'])
    plt.title('Average Consumption by Food Category and Gender')
    plt.xlabel('Food Category')
    plt.ylabel('Average Amount Consumed (g)')
    plt.legend(title='Gender')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_average_consumption_by_age_group(average_consumption_age_group, colors):
    average_consumption_age_group.T.plot(kind='barh', stacked=True, figsize=(14, 8), color=colors)
    plt.title('Average Consumption by Food Category and Age Group')
    plt.xlabel('Average Amount Consumed (g)')
    plt.ylabel('Age Group')
    plt.legend(title='Food Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def plot_population_pyramid(metric, ylabel, color_dict, df, NorkostVersion):
    desired_order = [
        'Fruits and nuts', 'Vegetables', 'Starchy vegetables', 'Grains and cereals', 'Legumes',
        'Dairy and alternatives', 'Eggs', 'Poultry', 'Red meat', 'Fish', 'Fats and oils',
        'Sweets and snacks', 'Miscellaneous'
    ]

    pivot_data = df.pivot_table(
        index=['AgeGroup', 'Gender'],
        columns='FoodCategory',
        values=metric,
        aggfunc='sum',
        fill_value=0
    )

    for category in desired_order:
        if category not in pivot_data.columns:
            pivot_data[category] = 0

    pivot_data = pivot_data[desired_order]
    pivot_data = pivot_data.sort_index(level='AgeGroup')

    fig, ax = plt.subplots(figsize=(14, 10))
    age_groups = sorted(df['AgeGroup'].unique())
    categories = desired_order

    for age_group in age_groups:
        for gender in ['Male', 'Female']:
            if (age_group, gender) in pivot_data.index:
                data = pivot_data.loc[(age_group, gender)]
            else:
                data = pd.Series(0, index=categories)

            cumulative = 0
            for category in categories:
                value = data[category]
                color = color_dict.get(category, '#333333')

                if gender == 'Male':
                    ax.barh(age_group, value, left=cumulative, color=color, edgecolor='none')
                    cumulative += value
                else:
                    ax.barh(age_group, -value, left=-cumulative, color=color, edgecolor='none')
                    cumulative += value

    ax.set_xlabel(ylabel)
    ax.set_ylabel('Age Group')
    ax.set_title(f'{ylabel} per capita by Age Group and Gender ({NorkostVersion})')
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_dict.get(category, '#333333')) for category in categories]
    labels = categories
    ax.legend(handles, labels, title='Food Categories', bbox_to_anchor=(1.05, 1), loc='upper left')
    max_value = pivot_data.sum(axis=1).max()
    ax.set_xlim(-max_value * 1.05, max_value * 1.05)
    ax.text(max_value * 0.8, len(age_groups), 'Male', ha='center', va='center', fontsize=12, color='blue')
    ax.text(-max_value * 0.8, len(age_groups), 'Female', ha='center', va='center', fontsize=12, color='red')
    ax.axvline(0, color='black', linewidth=0.5)
    plt.tight_layout()
    plt.show()
