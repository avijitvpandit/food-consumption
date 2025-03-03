#%%
##Importing the necessary libraries
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

#%%
# Load datasets
# Loading the data from the auxiliary folder
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auxillary')
nk2_filename = 'average percapita consumption_nk2.xlsx'
nk3_filename = 'average percapita consumption_nk3.xlsx'
nk2_df = pd.read_excel(os.path.join(file_path, nk2_filename))
nk3_df = pd.read_excel(os.path.join(file_path, nk3_filename))

# Add year columns
nk2_df['Year'] = 1994
nk3_df['Year'] = 2014

# Concatenate the two dataframes
nk_df = pd.concat([nk2_df, nk3_df], ignore_index=True)

# Data Cleaning and Preparation
# Handling missing values
nk_df.interpolate(method='linear', inplace=True)

# Set upper and lower limits for calorie consumption to remove outliers
calorie_lower_limit = 500
calorie_upper_limit = 4000
nk_df = nk_df[(nk_df['TotalCalories'] >= calorie_lower_limit) & (nk_df['TotalCalories'] <= calorie_upper_limit)]

# Basic exploration of the dataset
print(nk_df.head())
print(nk_df.describe())
#%%
# Concatenate the two dataframes
nk_df = pd.concat([nk2_df, nk3_df], ignore_index=True)

# Data Cleaning and Preparation
# Handling missing values
nk_df.interpolate(method='linear', inplace=True)

# Set upper and lower limits for calorie consumption to remove outliers
calorie_lower_limit = 500
calorie_upper_limit = 4000
nk_df = nk_df[(nk_df['TotalCalories'] >= calorie_lower_limit) & (nk_df['TotalCalories'] <= calorie_upper_limit)]

# Calculate proportions of food categories in terms of total calories
nk_df['Proportion'] = nk_df['TotalCalories'] / nk_df.groupby(['Year', 'AgeGroup', 'Gender'])['TotalCalories'].transform('sum')

# Basic exploration of the dataset
print(nk_df.head())
print(nk_df.describe())

# Analyze Changes Over Time (Temporal Trends)
# Comparing average proportion of food categories over years by gender and age group
food_categories = nk_df['FoodCategory'].unique()

for category in food_categories:
    plt.figure(figsize=(10, 5))
    category_data = nk_df[nk_df['FoodCategory'] == category]
    sns.lineplot(data=category_data, x='Year', y='Proportion', hue='Gender', style='AgeGroup', markers=True)
    plt.title(f'Proportion of Total Calories for {category} (1994 to 2014) by Gender and Age Group')
    plt.xlabel('Year')
    plt.ylabel('Proportion of Total Calories')
    plt.grid(True)
    plt.show()

# Fit Distribution to Changes in Dietary Consumption
# Fit normal distribution to Proportion for each year by Age Group and Gender
age_groups = nk_df['AgeGroup'].unique()
genders = nk_df['Gender'].unique()
years = nk_df['Year'].unique()

for year in years:
    for age_group in age_groups:
        for gender in genders:
            plt.figure(figsize=(10, 6))
            subset = nk_df[(nk_df['Year'] == year) & (nk_df['AgeGroup'] == age_group) & (nk_df['Gender'] == gender)]['Proportion']
            
            if len(subset) > 0:
                fit_params = stats.norm.fit(subset)

                x = np.linspace(subset.min(), subset.max(), 100)
                y = stats.norm.pdf(x, *fit_params)

                plt.plot(x, y, label=f'{year} Proportion (Normal Fit) - {age_group} - {gender}')
                plt.title(f'Fitted Normal Distribution for Proportion of Total Calories ({year}) - {age_group} - {gender}')
                plt.xlabel('Proportion of Total Calories')
                plt.ylabel('Density')
                plt.legend()
                plt.grid(True)
                plt.show()

# Model Trends Using Regression
# Polynomial regression to capture trends over time for Proportion by Age Group and Gender from 1994 to 2030
for age_group in age_groups:
    for gender in genders:
        for category in food_categories:
            subset = nk_df[(nk_df['AgeGroup'] == age_group) & (nk_df['Gender'] == gender) & (nk_df['FoodCategory'] == category)]
            if len(subset) > 1:
                poly = PolynomialFeatures(degree=2)
                X_years = subset['Year'].values.reshape(-1, 1)
                X_poly = poly.fit_transform(X_years)

                model = LinearRegression()
                model.fit(X_poly, subset['Proportion'].values)

                # Predicting and visualizing future trends
                pred_years = np.arange(1994, 2031).reshape(-1, 1)
                pred_years_poly = poly.transform(pred_years)
                predictions = model.predict(pred_years_poly)

                plt.figure(figsize=(10, 6))
                plt.plot(subset['Year'], subset['Proportion'], 'bo', label='Observed Data')
                plt.plot(pred_years, predictions, 'r-', label='Polynomial Fit')
                plt.title(f'Polynomial Regression for Proportion of Total Calories (1994 to 2030) - {age_group} - {gender} - {category}')
                plt.xlabel('Year')
                plt.ylabel('Proportion of Total Calories')
                plt.legend()
                plt.grid(True)
                plt.show()

# Scenario Analysis - Future Projection
# Predict consumption under various scenarios (e.g., increased awareness, economic growth)
# Placeholder for advanced scenario analysis based on different assumptions

print("Analysis complete. Future trends and scenario projections visualized.")