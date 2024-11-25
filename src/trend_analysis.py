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
calorie_lower_limit = 1200
calorie_upper_limit = 3000
nk_df = nk_df[(nk_df['TotalCalories'] >= calorie_lower_limit) & (nk_df['TotalCalories'] <= calorie_upper_limit)]

# Basic exploration of the dataset
print(nk_df.head())
print(nk_df.describe())

# Analyze Changes Over Time (Temporal Trends)
# Comparing average energy intake over years by gender
plt.figure(figsize=(12, 6))
sns.lineplot(data=nk_df, x='Year', y='AverageEnergyIntake', hue='Gender', marker='o')
plt.title('Average Energy Intake Over Time by Gender')
plt.xlabel('Year')
plt.ylabel('Average Energy Intake')
plt.grid(True)
plt.show()

# Analyzing Category-Wise Trends from 1994 to 2014
food_categories = nk_df['FoodCategory'].unique()

for category in food_categories:
    plt.figure(figsize=(10, 5))
    category_data = nk_df[nk_df['FoodCategory'] == category]
    sns.lineplot(data=category_data, x='Year', y='Average amount consumed (g)', hue='Gender', style='AgeGroup', markers=True)
    plt.title(f'Average Amount Consumed for {category} (1994 to 2014) by Gender and Age Group')
    plt.xlabel('Year')
    plt.ylabel('Average Amount Consumed (g)')
    plt.grid(True)
    plt.show()

# Fit Distribution to Changes in Dietary Consumption
# Fit normal distribution to TotalCalories for each year by Age Group and Gender
age_groups = nk_df['AgeGroup'].unique()
genders = nk_df['Gender'].unique()
years = nk_df['Year'].unique()

for year in years:
    for age_group in age_groups:
        for gender in genders:
            plt.figure(figsize=(10, 6))
            subset = nk_df[(nk_df['Year'] == year) & (nk_df['AgeGroup'] == age_group) & (nk_df['Gender'] == gender)]['TotalCalories']
            
            if len(subset) > 0:
                fit_params = stats.norm.fit(subset)

                x = np.linspace(subset.min(), subset.max(), 100)
                y = stats.norm.pdf(x, *fit_params)

                plt.plot(x, y, label=f'{year} Total Calories (Normal Fit) - {age_group} - {gender}')
                plt.title(f'Fitted Normal Distribution for Total Calories ({year}) - {age_group} - {gender}')
                plt.xlabel('Total Calories')
                plt.ylabel('Density')
                plt.legend()
                plt.grid(True)
                plt.show()

# Model Trends Using Regression
# Polynomial regression to capture trends over time for TotalCalories by Age Group and Gender from 1994 to 2030
for age_group in age_groups:
    for gender in genders:
        subset = nk_df[(nk_df['AgeGroup'] == age_group) & (nk_df['Gender'] == gender)]
        if len(subset) > 1:
            poly = PolynomialFeatures(degree=2)
            X_years = subset['Year'].values.reshape(-1, 1)
            X_poly = poly.fit_transform(X_years)

            model = LinearRegression()
            model.fit(X_poly, subset['TotalCalories'].values)

            # Predicting and visualizing future trends
            pred_years = np.arange(1994, 2031).reshape(-1, 1)
            pred_years_poly = poly.transform(pred_years)
            predictions = model.predict(pred_years_poly)

            plt.figure(figsize=(10, 6))
            plt.plot(subset['Year'], subset['TotalCalories'], 'bo', label='Observed Data')
            plt.plot(pred_years, predictions, 'r-', label='Polynomial Fit')
            plt.title(f'Polynomial Regression for Total Calories Trend (1994 to 2030) - {age_group} - {gender}')
            plt.xlabel('Year')
            plt.ylabel('Total Calories Per Capita')
            plt.legend()
            plt.grid(True)
            plt.show()



# %%
