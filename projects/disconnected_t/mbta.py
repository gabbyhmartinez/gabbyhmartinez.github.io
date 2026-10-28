"""
Author: Gabby Martinez

File: mbta.py

Description: 
    Analysis of MBTA data and Boston demographic data for ENGW3308 
    Project 2. Filters data and seeks to answer questions related to 
    accessibility of the T to Bostonians.
    
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

RIDERSHIP_MODE = "/Users/gabbymartinez/Documents/ENGW Research Project/data_analysis/MBTA_Monthly_Ridership_By_Mode.csv"
SERVICE_ALERTS = "/Users/gabbymartinez/Documents/ENGW Research Project/data_analysis/MBTA_Service_Alerts.csv"
SATISFACTION = "/Users/gabbymartinez/Documents/ENGW Research Project/data_analysis/MBTA_Service_Customer_Satisfaction.csv"
DEMOGRAPHICS = "/Users/gabbymartinez/Documents/ENGW Research Project/data_analysis/redistricting_data_tract20_nbhd_hhpopsize_ab-1.csv"

def clean_df(df, features, method=""):
    ''' 
    Takes a dataframe and returns it with only the features
    that are desired to use further.
    '''
    if method == "":
        df = df[features]
    if method == "drop":
        for header in features:
            df = df.drop(header, axis=1)
            
    return df

def clean_time(df, column_name):
    ''' 
    Changes the date/time column in a dataframe to one that
    includes YYYY/MM/DD format. 
    '''
    # Initialize new list for cleaned date 
    cleaned_dates = []
    
    # Clean dates and append to list
    for date in df[column_name]:
        # Remove the `+00` part from the string
        date = date.split("+")[0].strip()
        datetime_object = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
        date_only = datetime_object.strftime("%Y/%m/%d")
        cleaned_dates.append(date_only)
        
    return cleaned_dates

def highest_ridership(df):
    ''' 
    Given the ridership mode dataframe, returns a dictionary in which
    the keys are each year there is data for, and the values are a list 
    with the mode of transportation with the most riders for that year
    and the number of riders for that year.
    '''
    # List of years to loop through
    years = ['2016', '2017', '2018', '2019', '2020', 
             '2021', '2022', '2023', '2024']
    
    # Dictionary to store year and highest rider info
    most_riders = {}
    
    for year in years:
        # Filter for rows in the specified year
        df['year'] = df['clean_date'].str[:4]
        yearly_data = df[df['year'] == year]
        
        # Group data by route/line
        groups = yearly_data.groupby('route_or_line')
        
        # Add up total riders for each month by route/line
        totals = groups['total_monthly_ridership'].sum()
        
        # Find which route has the highest sum
        max_route = totals.sort_values(ascending=False).index[0]
        max_ridership = totals.max()
        
        # Add year and route/ridership number info to dictionary
        most_riders[year] = [max_route, max_ridership]
        
    
    return most_riders

def lowest_ridership(df):
    ''' 
    Given the ridership mode dataframe, returns a dictionary in which
    the keys are each year there is data for, and the values are a list 
    with the mode of transportation with the fewest riders for that year
    and the number of riders for that year. Excludes boat and ferry 
    information.
    '''
    # List of years to loop through
    years = ['2016', '2017', '2018', '2019', '2020', 
             '2021', '2022', '2023', '2024']
    
    # Dictionary to store year and highest rider info
    least_riders = {}
    
    for year in years:
        # Filter for rows in the specified year
        df['year'] = df['clean_date'].str[:4]
        yearly_data = df[df['year'] == year]
        
        # Exclude boats, ferry, the ride
        exclude_modes = ['Boat-F1', 'Boat-F3', 'Boat-F4', "Ferry", "The RIDE"]
        yearly_data = yearly_data[~yearly_data['mode'].isin(exclude_modes)]
        
        # Group data by route/line
        groups = yearly_data.groupby('route_or_line')
        
        # Add up total riders for each month by route/line
        totals = groups['total_monthly_ridership'].sum()
        
        # Find which route has the highest sum
        min_route = totals.sort_values(ascending=True).index[0]
        min_ridership = totals.min()
        
        # Add year and route/ridership number info to dictionary
        least_riders[year] = [min_route, min_ridership]
        
    return least_riders

def most_alerts(df):
    ''' 
    Given the dataframe, returns a dictionary that has the years and
    mode of transportation with the most service alerts for that year. 
    '''
    # Initialize dictionary
    most_alerts = {}
    
    # Extract year column from 'clean_date' if not already extracted
    df['year'] = df['clean_date'].str[:4]
    
    # Group by year and gui_mode_name, then count occurrences
    mode_counts = df.groupby(['year', 'gui_mode_name', 'cause_name']).size().\
    reset_index(name='count')

    # For each year, find the mode with the maximum count
    for year in mode_counts['year'].unique():
        yearly_data = mode_counts[mode_counts['year'] == year]
        most_frequent_mode = yearly_data.loc[yearly_data['count'].idxmax()]
        most_alerts[year] = [most_frequent_mode['gui_mode_name'], 
                             most_frequent_mode['count'], 
                             most_frequent_mode['cause_name']]
    
    return most_alerts
    
def delay_time(df):
    ''' 
    Counts number of delays that are up to 15 minutes or more.
    '''
    # Initialize count for delays over 15 mins
    count = 0
    
    # Loop through column to count delays
    for delay in df['severity_name']:
        if delay != "up to 10 minutes" and delay != "up to 15 minutes":
            count += 1
            
    return count

def delay_type(df):
    ''' 
    Given a dataframe and mode of transport, finds what the 
    most common service delay is.
    '''
    modes = ['Access', 'Bus', 'Commuter Rail', 'Subway', 'Boat', 'Systemwide']
    modes_dct = {}
    
    for mode in modes:
        # Filter the dataframe for the specified mode of transportation
        mode_data = df[df['gui_mode_name'] == mode]
    
        # Get most frequent delay for mode of transport
        most = mode_data['cause_name'].mode().iloc[0]
        modes_dct[mode] = most
    
    return modes_dct
        
def delay_code(df):
    ''' 
    Given the service alert dataframe, finds what modes of transportation
    have the most serve delay ratings. 
    '''
    modes = ['Access', 'Bus', 'Commuter Rail', 'Subway', 'Boat', 'Systemwide']
    codes_dct = {}
    
    for mode in modes:
        # Filter the dataframe for the specified mode of transportation
        mode_data = df[df['gui_mode_name'] == mode]
    
        # Calculate and return the average of the "number" column for that mode
        average = mode_data['severity_code'].mean()
        codes_dct[mode] = round(average, 2)
    
    return codes_dct
    
def rating_over_time(df, question):
    ''' 
    Finds how overall rating of the mbta has changed over time. Returns
    a graph showing dissatisfied and satisfied percentages for each year.
    '''
    
    # List of years to loop through
    years = ['2016', '2017', '2018', '2019', '2020', 
             '2021', '2022', '2023', '2024']
    
    # List to plot
    dissatisfied = []
    satisfied = []
    n = []
    
    # Convert 'survey_date' to string and extract 'year'
    df['year'] = df['survey_date'].astype(str).str[:4]

    
    # Loop through data in each year to plot
    for year in years:
        # Filter for rows in the specified year and question
        yearly_data = df[(df['year'] == year) & (df["question_description"] 
                                                 == question)]
        
        # Sum the specified columns for dissatisfaction (1, 2, 3) and satisfaction (5, 6, 7)
        dissatisfaction_percentage = yearly_data[['response_1_percent', 
                                                  'response_2_percent', 
                                                  'response_3_percent']].sum(axis=1)
        satisfaction_percentage = yearly_data[['response_5_percent', 
                                               'response_6_percent', 
                                               'response_7_percent']].sum(axis=1)
        neutral = yearly_data[['response_4_percent']].sum(axis=1)
        
        # Average the sums across all rows for the year
        avg_dissatisfaction = dissatisfaction_percentage.mean()
        avg_satisfaction = satisfaction_percentage.mean()
        avg_neutral = neutral.mean()
        
        # Append the average values for dissatisfaction and satisfaction
        dissatisfied.append(avg_dissatisfaction)
        satisfied.append(avg_satisfaction)
        n.append(avg_neutral)
    
    # plot data
    # Define bar width and positions
    bar_width = 0.20
    index = np.arange(len(years))
    
    # Plot the bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(index, dissatisfied, bar_width, label="Dissatisfied (%)", 
            color='red')
    plt.bar(index + bar_width, satisfied, bar_width, label="Satisfied (%)", 
            color='green')
    plt.bar(index + 2 * bar_width, n, bar_width, label="Neutrtal (%)",
            color='gray')
    
    # Labeling
    plt.xlabel("Year")
    plt.ylabel("Percentage")
    plt.title(f"Satisfaction over Time for '{question}'")
    plt.xticks(index + bar_width / 2, years)
    plt.grid()
    plt.legend()

    plt.savefig("rating_over_time.png", bbox_inches='tight')
    plt.show()
    
def percent_race(df, race):
    ''' 
    Given the demographics dataframe and the race to calculate, 
    returns a dictionary of the nieghborhoods and their percentage
    of the population that is the given race. 
    '''
    race_dct = {}
    
    # Loop through each row in the DataFrame
    for _, row in df.iterrows():
        neighborhood = row['field concept']
        # Calculate percentage for the specified race for each neighborhood
        percent = (row[race] / row['total_population']) * 100
        race_dct[neighborhood] = round(percent, 2)
           
    return race_dct

def sort_race_data(white_dct, black_dct, hisp_dct, asian_dct):
    ''' 
    Given the dictionaries of neighborhoods and their percentage of 
    a certain race, returns a new dictionary for each neighborhood with
    each racial percentage sorted in decensing order. 
    '''
    race_data = {}
    
    for neighborhood, white_percent in white_dct.items():
        # Create a dictionary for each neighborhood with labeled racial %s
        unsorted_race_dict = {
            'White': white_percent,
            'Black': black_dct.get(neighborhood, 0),
            'Hispanic': hisp_dct.get(neighborhood, 0),
            'Asian': asian_dct.get(neighborhood, 0)
            }
        
        # Sort the dictionary by percentage in descending order
        sorted_race_dict = dict(sorted(unsorted_race_dict.items(), 
                                       key=lambda item: item[1], 
                                       reverse=True))
        
        race_data[neighborhood] = sorted_race_dict
    
    return race_data

def most_prisons(df):
    ''' 
    Finds what neighborhoods have the highest prison
    populations. 
    '''
    adult_facilities = {}
    juvenile_facilities = {}
    
    for _, row in df.iterrows():
        neighborhood = row['field concept']
        # Find which neighborhoods have adult facilities
        if row['Correctional facilities for adults'] != 0:
            adult_facilities[neighborhood] = row['Correctional facilities for adults']
        # Find which neighborhoods have juveline facilities
        if row['Juvenile facilities'] != 0:
            juvenile_facilities[neighborhood] = row['Juvenile facilities']
    return adult_facilities, juvenile_facilities

def most_education(df):
    ''' 
    Finds what neighborhoods have university housing, and therefore
    a higher student population/more education population. 
    '''
    education = {}
    
    for _,row in df.iterrows():
        neighborhood = row['field concept']
        # Find nieghborhoods with university housing
        if row['College/University student housing'] != 0:
            education[neighborhood] = row['College/University student housing']
            
    return education

def population_plot(dct):
    ''' 
    Plots all the race population percentages for each neighborhood. 
    '''
    # Prepare data for plotting
    neighborhoods = list(dct.keys())
    white_pct = [dct[nbhd].get('White', 0) for nbhd in neighborhoods]
    asian_pct = [dct[nbhd].get('Asian', 0) for nbhd in neighborhoods]
    hispanic_pct = [dct[nbhd].get('Hispanic', 0) for nbhd in neighborhoods]
    black_pct = [dct[nbhd].get('Black', 0) for nbhd in neighborhoods]
    
    # Position of the bars on the x-axis
    x = np.arange(len(neighborhoods))
    
    # Plotting
    plt.figure(figsize=(15, 8), dpi=400)
    bar_width = 0.85
    
    # Stacked bar chart
    plt.bar(x, white_pct, color='deepskyblue', width=bar_width, label='White')
    plt.bar(x, asian_pct, bottom=white_pct, color='orange', width=bar_width, 
            label='Asian')
    plt.bar(x, hispanic_pct, bottom=np.array(white_pct) + np.array(asian_pct), 
            color='green', width=bar_width, label='Hispanic')
    plt.bar(x, black_pct, bottom=np.array(white_pct) + np.array(asian_pct) + 
            np.array(hispanic_pct), color='hotpink', width=bar_width, 
            label='Black')
    
    # Labels and title
    plt.xlabel("Neighborhood")
    plt.ylabel("Population Percentage")
    plt.title("Racial Composition by Neighborhood")
    plt.xticks(x, neighborhoods, rotation=90)
    plt.yticks(np.arange(0, 110, step=10))
    plt.grid(axis='y')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("race_percentages.png")
    plt.show()
    
def alerts_plot(dct):
    ''' 
    Given the dictionary of mode with most service alerts, plots
    a scatter plot with the mode and number of service alerts for each year.
    '''
    # Prepare data for the plot
    years = list(dct.keys())
    alerts = [dct[year][1] for year in years]
    modes = [dct[year][0] for year in years]
    
    # Create the scatter plot using plt.scatter
    plt.figure(figsize=(10, 6), dpi=400)
    plt.bar(years, alerts)
    
    # Customize the plot
    plt.xlabel('Year')
    plt.ylabel('Number of Service Alerts')
    plt.title('Service Alerts Over Time for the Bus')
    
    plt.savefig("alerts.png")
    plt.show()

def severity_code_plot(dct):
    ''' 
    Given the average severity code per mode of transportation, creates
    a bar chart.
    '''
    # Get x and y (mode of transportation and avg codes)
    mode = list(dct.keys())
    value = list(dct.values())
    
    # Create plot
    plt.figure(figsize=(10, 6), dpi=400)
    plt.bar(mode, value, color="orangered")
    
    # Labels and title
    plt.xlabel("Mode of Transportation")
    plt.ylabel("Average Severity Code")
    plt.title("Average Severity Code for Service Alerts by Mode")
    plt.grid(axis='y')
    
    plt.savefig("severity_codes.png")
    plt.show()
    
    
def ridership_numbers_plot(highest_dct, lowest_dct):
    ''' Given the dictionary with the highest ridership mode and numbers,
    and the dictionary with the lowest ridership mode and numbers, creates
    a bar chart. 
    '''
    # Prepare data
    years = list(highest_dct.keys())
    
    highest_mode = [value[0] for value in highest_dct.values()]
    highest_num = [value[1] for value in highest_dct.values()]
    
    lowest_mode = [value[0] for value in lowest_dct.values()]
    lowest_num = [value[1] for value in lowest_dct.values()]
    
    # Set the bar width and positions
    bar_width = 0.4
    index = range(len(years))
    
    # Create plot
    plt.figure(figsize=(10, 6), dpi=400)
    plt.bar(index, highest_num, width=bar_width, color="blue", 
            label="Highest Ridership (Bus)")
    plt.bar([i + bar_width for i in index], lowest_num, width=bar_width, 
            color="red", label="Lowest Ridership (Silver Line)")
    
    # Labels
    plt.xlabel('Year')
    plt.ylabel('Ridership Numbers')
    plt.title('Highest and Lowest Ridership Numbers by Year')
    
    # Add x-tick labels (Years)
    plt.xticks([i + bar_width / 2 for i in index], years)
    
    plt.legend()
    plt.tight_layout()
    plt.savefig("ridership_numbers.png")
    plt.show()
    

def main():
    # Read datasets into dataframes
    ridership_mode = pd.read_csv(RIDERSHIP_MODE)
    service_alerts = pd.read_csv(SERVICE_ALERTS)
    satisfaction = pd.read_csv(SATISFACTION)
    neighborhood_dems = pd.read_csv(DEMOGRAPHICS, skiprows=1)
    
    # Ridership Mode
    mode_features = ["service_date", "mode", "route_or_line", 
                     "total_monthly_ridership", "average_monthly_ridership"]
    ridership_mode = clean_df(ridership_mode, mode_features)
    
    # Service Alters
    alert_features = ["gui_mode_name", "effect_name", "cause_name",
                      "cause_code", "severity_name", "severity_code",
                      "service_effect_text", "notif_start"]
    service_alerts = clean_df(service_alerts, alert_features)
    
    # Satisfaction Survey
    drop_features = ["survey_name", "ObjectId"]
    satisfaction = clean_df(satisfaction, drop_features, "drop")
    
    # Clean columns as needed
    # Ridership Mode
    time = clean_time(ridership_mode, "service_date")
    ridership_mode['clean_date'] = time
    
    # Service alerts
    time_service = clean_time(service_alerts, "notif_start")
    service_alerts["clean_date"] = time_service
    
    # Satisfaction Survey
    satisfaction = satisfaction.dropna(subset=["question_description"])
    
    # Neighborhood dem df
    neighborhood_dems = neighborhood_dems.rename(columns={
        neighborhood_dems.columns[1]: 'total_population', 
        neighborhood_dems.columns[2]: 'white_population',
        neighborhood_dems.columns[3]: 'black_population',
        neighborhood_dems.columns[4]: 'hispanic_population',
        neighborhood_dems.columns[5]: 'asian_population',
        neighborhood_dems.columns[6]: 'mixed/other'})


    # Analysis!! Some questions to answer:
    # What ridership mode has highest total monthlthy ridership for each year?
    most_riders = highest_ridership(ridership_mode)
    print(f"Highest ridership for each year: {most_riders}")
    
    # What line has the least?
    least_riders = lowest_ridership(ridership_mode)
    print(f"Lowest ridership for each year: {least_riders}")
    
    # Which gui_mode_name has the most service alerts each year?
    most_alerts_line = most_alerts(service_alerts)
    print(f"Mode with most service alerts: {most_alerts_line}")
    
    # How many delays are up to x amount of time? (15,20 minutes?) severity name
    delays = delay_time(service_alerts)
    print(f"Number of delays up to 20 minutes or more: {delays}")
    
    # Average severity per mode of transportation
    codes = delay_code(service_alerts)
    print(f"Average severity code per mode: {codes}")
    
    # Most common delay for each mode?
    delay_causes = delay_type(service_alerts)
    print(f"Most common delay reasons per mode: {delay_causes}")
    
    # How has overall rating of the mbta changed over time?
    rating_over_time(satisfaction, 'How would you rate the mbta overall?')
    
    # Which neighborhoods have the highest white pop?
    white_pop = percent_race(neighborhood_dems, "white_population")
    
    black_pop = percent_race(neighborhood_dems, "black_population")
    
    hisp_pop = percent_race(neighborhood_dems, "hispanic_population")
    
    asian_pop = percent_race(neighborhood_dems, "asian_population")
    
    sort_pop = sort_race_data(white_pop, black_pop, hisp_pop, asian_pop)
    print(f"Populations each town: {sort_pop}")
    
    # Which neighborhoods have the most prisons/prisoners?
    adult, juvenile = most_prisons(neighborhood_dems)
    print(f"Neighborhoods with adult correctional facilities: {adult}")
    print(f"Neighborhoods with juvenile correctional facilites: {juvenile}")
    
    # Which neighborhoods have the most educated pop?
    student_housing = most_education(neighborhood_dems)
    print(f"Neighborhoods with student housing: {student_housing}")
    
    
    # Make some more graphs!
    # Racial percentages for each neighborhood
    population_plot(sort_pop)
    
    # Number service alerts for bus over the years
    alerts_plot(most_alerts_line)
    
    # Average severity code graph
    severity_code_plot(codes)
    
    # Highest vs lowest ridership graph
    ridership_numbers_plot(most_riders, least_riders)
    
    
if __name__ == "__main__":
    main()
