import pandas as pd
import json

leagues = ['E0', 'D1', 'I1', 'SP1', 'F1']

years = ['0001', '0102', '0203', '0304', '0405', '0506', '0607', '0708', '0809', '0910', 
         '1011', '1112', '1213', '1314', '1415', '1516', '1617', '1718', '1819', '1920', 
         '2021', '2122', '2223', '2324', '2425']

def create_teams_dict(fix_df: pd.DataFrame):
    '''Function that takes in a dataframe of fixtures and returns a dictionary of all teams by season'''

    seasons = fix_df['season'].unique().tolist()
    teams_dict = {year: [] for year in years}

    for year in years:
        teams = fix_df.loc[fix_df['season'] == year]['HomeTeam'].unique().tolist()
        teams_dict[year] = teams

    return teams_dict

def get_rel_prom_teams(teams_dict):
    '''Takes in a dictionary listing all teams by season, and returns a dictionary of which teams were relegated'''

    rel_prom_dict = {year: {'relegated': [], 'promoted': []} for year in years[:-1]}

    for i, year in enumerate(years[:-1]):

        for team in teams_dict[year]:
            if team not in teams_dict[years[i+1]]:
                rel_prom_dict[year]['relegated'].append(team)

        for team in teams_dict[years[i+1]]:
            if team not in teams_dict[year]:
                rel_prom_dict[year]['promoted'].append(team)

    return rel_prom_dict

all_rel_prom_teams = {}

for league in leagues:

    league_df = pd.read_pickle(f'football-poisson-prediction/data/europe/{league}_00-01_to_24-25.pkl')

    league_teams = create_teams_dict(league_df)

    league_rel_prom = get_rel_prom_teams(league_teams)

    all_rel_prom_teams[league] = league_rel_prom

with open('football-poisson-prediction/data/europe/rel_prom_teams.json', 'w') as json_file:
    json.dump(all_rel_prom_teams, json_file, indent=4)