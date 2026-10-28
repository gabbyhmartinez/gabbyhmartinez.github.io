"""
Name: Gabby Martinez

File: japan_research_final.py

Description: Plotting data for life expectancy and radiation levels of
prefectures in Japan for different years. Determining correlation and 
statistical significance using regression lines and analysis.

"""

# Import statements
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np
from scipy import stats

def load_data(file_path):
    """Load data from a CSV file and organize it by year."""
    data = {"2010": [], "2015": [], "2020": []}
    with open(file_path, "r") as file:
        file.readline()  # Skip the header
        for line in file:
            line = line.strip().split(",")
            year = line[1]
            if year in data:
                data[year].append(line)
    return data

def prepare_graph_data(year_data):
    """Extract required columns (prefecture, life expectancy, radiation) 
    for a specific year."""
    graph_data = []
    for line in year_data:
        prefecture = line[0]
        life_exp = float(line[4])
        radiation = float(line[6]) if line[6] != "#VALUE!" else None
        if radiation is not None:
            graph_data.append([prefecture, life_exp, radiation])
    return graph_data

def extract_regression_data(graph_data):
    """Separate life expectancy and radiation data for regression."""
    life_exp = [line[1] for line in graph_data]
    radiation = [line[2] for line in graph_data]
    return radiation, life_exp

def plot_graph(data, title, radiation_all, life_exp_all, regions, 
               region_colors):
    """Plot life expectancy vs radiation level with regression line."""
    plt.figure(figsize=(6, 4), dpi=200)
    plotted_regions = set()

    for line in data:
        prefecture, life_exp, radiation = line
        if prefecture not in regions:
            continue

        region = regions[prefecture]
        color = region_colors[region]

        plt.scatter(radiation, life_exp, color=color)
        if region not in plotted_regions:
            plt.scatter([], [], color=color, label=region)
            plotted_regions.add(region)

    coefficients = np.polyfit(radiation_all, life_exp_all, 1)
    poly = np.poly1d(coefficients)
    x_reg = np.linspace(min(radiation_all), max(radiation_all), 100)
    y_reg = poly(x_reg)
    plt.plot(x_reg, y_reg, color='black', linewidth=1, linestyle='-')

    for line in data:
        prefecture, life_exp, radiation = line
        if prefecture in ['Fukushima', 'Hiroshima']:
            plt.annotate(prefecture, xy=(radiation, life_exp), 
                         xytext=(radiation + 0.01, life_exp + 0.01),
                         arrowprops=dict(facecolor='black', edgecolor='black', 
                                         linestyle=':',
                                         linewidth=1, shrink=0.02, width=0.5, 
                                         headwidth=4, headlength=4))

    plt.xlabel('Radiation Level (\u00B5Sv)')
    plt.ylabel('Life Expectancy (years)')
    plt.title(title)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)

def calculate_correlation_significance(data, year):
    """Calculate and display the correlation between radiation and life 
    expectancy."""
    radiation_all, life_exp_all = extract_regression_data(data)
    correlation, _ = stats.pearsonr(radiation_all, life_exp_all)
    n = len(radiation_all)
    t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2))
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=n-2))

    significance = "significant" if p_value < 0.05 else "not significant"
    print(f"{year}:")
    print(f"Correlation coefficient: {correlation}")
    print(f"T-statistic: {t_stat}")
    print(f"P-value: {p_value}")
    print(f"The correlation is {significance} at the 0.05 level.")
    return correlation, p_value

def calculate_life_expectancy_difference(graph_2010, graph_2020):
    """Calculate the change in life expectancy between 2010 and 2020."""
    data_2010_dict = {line[0]: line[1] for line in graph_2010}
    data_2020_dict = {line[0]: line[1] for line in graph_2020}

    difference_list = []
    for prefecture, life_exp_2010 in data_2010_dict.items():
        if prefecture in data_2020_dict:
            life_exp_2020 = data_2020_dict[prefecture]
            difference = life_exp_2020 - life_exp_2010
            difference_list.append((prefecture, difference))
    return sorted(difference_list, key=lambda x: x[1], reverse=True)

def plot_life_expectancy_difference(difference_list, plot_list):
    """Create a bar chart showing the differences in life expectancy."""
    prefecture, change, colors = [], [], []
    for line in difference_list:
        if line[0] in plot_list:
            prefecture.append(line[0])
            change.append(line[1])
            colors.append(plot_list[line[0]])

    plt.figure(figsize=(6, 4), dpi=200)
    bar_width = 0.5
    plt.bar(prefecture, change, width=bar_width, color=colors)
    plt.grid(axis='y')
    plt.xlabel("Prefecture")
    plt.xticks(rotation=90, fontsize=8)
    plt.ylabel("Life Expectancy Growth")
    plt.title("Difference in Life Expectancy from 2010-2020 by Prefecture")
    plt.savefig("life_difference.png", bbox_inches='tight')
    plt.show()

def main():
    # Load and prepare data
    data = load_data("Japan Life Expectancy Data 2.0.csv")
    graph_2010 = prepare_graph_data(data["2010"])
    graph_2015 = prepare_graph_data(data["2015"])
    graph_2020 = prepare_graph_data(data["2020"])

    r_regression2010, l_regression2010 = extract_regression_data(graph_2010)
    r_regression2015, l_regression2015 = extract_regression_data(graph_2015)
    r_regression2020, l_regression2020 = extract_regression_data(graph_2020)

    regions = {
        'Hokkaido': 'Hokkaido',
        'Aomori': 'Tohoku', 'Iwate': 'Tohoku', 'Miyagi': 'Tohoku', 'Akita': 
            'Tohoku', 'Yamagata': 'Tohoku', 'Fukushima': 'Tohoku',
        'Ibaraki': 'Kanto', 'Tochigi': 'Kanto', 'Gunma': 'Kanto', 'Saitama': 
            'Kanto', 'Chiba': 'Kanto', 'Tokyo': 'Kanto', 'Kanagawa': 'Kanto',
        'Niigata': 'Chubu', 'Toyama': 'Chubu', 'Ishikawa': 'Chubu', 'Fukui': 
            'Chubu', 'Yamanashi': 'Chubu', 'Nagano': 'Chubu', 'Gifu': 'Chubu', 
            'Shizuoka': 'Chubu', 'Aichi': 'Chubu',
        'Mie': 'Kinki', 'Shiga': 'Kinki', 'Kyoto': 'Kinki', 'Osaka': 'Kinki', 
        'Hyogo': 'Kinki', 'Nara': 'Kinki', 'Wakayama': 'Kinki',
        'Tottori': 'Chugoku', 'Shimane': 'Chugoku', 'Okayama': 'Chugoku', 
        'Hiroshima': 'Chugoku', 'Yamaguchi': 'Chugoku',
        'Tokushima': 'Shikoku', 'Kagawa': 'Shikoku', 'Ehime': 'Shikoku', 
        'Kochi': 'Shikoku',
        'Fukuoka': 'Kyushu', 'Saga': 'Kyushu', 'Nagasaki': 'Kyushu', 
        'Kumamoto': 'Kyushu', 'Oita': 'Kyushu', 'Miyazaki': 'Kyushu', 
        'Kagoshima': 'Kyushu', 'Okinawa': 'Kyushu'}

    region_colors = {
        'Hokkaido': 'blue', 'Tohoku': 'green', 'Kanto': 'red', 
        'Chubu': 'purple', 'Kinki': 'orange', 'Chugoku': 'black', 
        'Shikoku': 'pink', 'Kyushu': 'yellow'}

    # Generate graphs and calculate correlations
    for year, graph_data, r_regression, l_regression in zip(
        ["2010", "2015", "2020"],
        [graph_2010, graph_2015, graph_2020],
        [r_regression2010, r_regression2015, r_regression2020],
        [l_regression2010, l_regression2015, l_regression2020]):

        plot_graph(graph_data, f"Life Expectancy vs Radiation Level {year}",
                   r_regression, l_regression, regions, region_colors)
        plt.savefig(f"life_vs_radiation{year}.png", bbox_inches='tight')
        plt.show()
        calculate_correlation_significance(graph_data, year)

    # Calculate and plot life expectancy differences
    difference_list = calculate_life_expectancy_difference(graph_2010,
                                                           graph_2020)

    plot_list = {
        'Tottori': 'blue', 'Hyogo': 'blue', 'Shiga': 'blue', 
        'Ishikawa': 'blue', 'Kyoto': 'blue', 'Fukushima': 'purple',
        'Miyazaki': 'red', 'Niigata': 'red', 'Fukui': 'red', 
        'Okinawa': 'red', 'Kumamoto': 'red', 'Hiroshima': 'purple'}

    plot_life_expectancy_difference(difference_list, plot_list)

main()
