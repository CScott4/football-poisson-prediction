import pandas as pd
import requests
import io

# We will import historical data including scores and betting odds from football-data.co.uk
# Explanations of the data fields can be found at https://www.football-data.co.uk/notes.txt
base_url = 'https://www.football-data.co.uk/mmz4281/'

# No betting odds are available before the 2000/01 season, so that is where we start
years = ['0001', '0102', '0203', '0304', '0405', '0506', '0607', '0708', '0809', '0910', 
         '1011', '1112', '1213', '1314', '1415', '1516', '1617', '1718', '1819', '1920', 
         '2021', '2122', '2223', '2324', '2425']

# E0 denotes the English Premier League. E1, E2, E3, and EC can be used for the Championship, League 1, League 2, and Conference.
# Other codes, e.g. D1 and D2 for Bundeliga 1 and 2, can be used for other countries' leagues
leagues = ['E0', 'D1', 'I1', 'SP1', 'F1'] 

df_dict = {div: pd.DataFrame() for div in leagues}

for league in leagues:
    league_df = pd.DataFrame()
    for year in years:
        response = requests.get(f'{base_url}{year}/{league}.csv')

        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            
            df = pd.read_csv(csv_data, on_bad_lines='skip')
            df['season'] = year

            league_df = pd.concat([league_df, df])
    df_dict[league] = league_df

    # Deal with differences in data across different years
    league_df['Div'].fillna(league_df['ï»¿Div'], inplace=True)

    # Select columns I want
    league_df = league_df[['Div', 'season', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'WHH', 'WHD', 'WHA']].copy()

    league_df.dropna(inplace=True)

    league_df['Date'] = pd.to_datetime(league_df['Date'], dayfirst=True)

    league_df.reset_index(drop=True, inplace=True)

    league_df['FTHG'] = league_df['FTHG'].astype(int)
    league_df['FTAG'] = league_df['FTAG'].astype(int)

    # Save to pickle
    league_df.to_pickle(f'football-poisson-prediction/data/europe/{league}_00-01_to_24-25.pkl')