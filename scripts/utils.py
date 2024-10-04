# This file contains functions for use in the notebooks in order to populate stats, simulate games etc.
# This will be useful for testing the method on different leagues
import pandas as pd
import numpy as np
from scipy.stats import poisson

def populate_team_stats(fixtures: pd.DataFrame, rel_prom_teams):

    all_teams = fixtures['HomeTeam'].unique().tolist()

    # Each team will have a list of their previous 19 performance multipliers
    # Stats will be calculated as the mean of these performance ratings
    # Each time a team plays, their newest performance multipliers will be added to the lists and the oldest will be popped from the lists
    # Each team also has a counter of how many games we have to calculate stats from. This will be use to mark more uncertain predictions 
    stats_dict = {team: {'off': [1.0] * 19, 'def': [1.0] * 19, 'count': 0} for team in all_teams}

    # Similar system for averages, starting with an estimate
    avg_dict = {'home': [1.7] * 190, 'away': [1.2] * 190}

    # Initialise columns for stats
    fixtures[['h_avg', 'a_avg', 'h_off', 'h_def', 'a_off', 'a_def', 'uncertain']] = 1.0

    current_season = "0001" # Tracking season so that promoted/relegated teams can be dealt with
    for i, row in fixtures.iterrows():

        season = row['season']
        h_team, a_team = row['HomeTeam'], row['AwayTeam']
        h_goals, a_goals = row['FTHG'], row['FTAG']
        uncertain = 0

        # Check if new season
        if season != current_season:
            
            # Calculate average stats of relegated teams
            relegated_off_avg = np.mean([np.mean(stats_dict[team]['off']) for team in rel_prom_teams[current_season]['relegated']])
            relegated_def_avg = np.mean([np.mean(stats_dict[team]['def']) for team in rel_prom_teams[current_season]['relegated']])

            # Attribute to promoted teams
            for team in rel_prom_teams[current_season]['promoted']:
                stats_dict[team]['off'] = [relegated_off_avg] * 19
                stats_dict[team]['def'] = [relegated_def_avg] * 19
                stats_dict[team]['count'] = 0 # Reset count to zero in case a previously relegated team is promoted back up. I only want to use recent data.

            # Update current season
            current_season = season

        # Calculate team stats and averages prior to current game
        h_avg, a_avg = np.mean(avg_dict['home']), np.mean(avg_dict['away'])
        h_off, h_def = np.mean(stats_dict[h_team]['off']), np.mean(stats_dict[h_team]['def'])
        a_off, a_def = np.mean(stats_dict[a_team]['off']), np.mean(stats_dict[a_team]['def'])

        # Mark uncertain games
        if stats_dict[h_team]['count'] < 19 or stats_dict[a_team]['count'] < 19:
            uncertain = 1

        # Update fixture stats
        fixtures.loc[i, ['h_avg', 'a_avg', 'h_off', 'h_def', 'a_off', 'a_def', 'uncertain']] = [h_avg, a_avg, h_off, h_def, a_off, a_def, uncertain]

        # Calculate performance multipliers for this game
        # A performance rating takes the opponent's quality into account. It is the multiplier of how they performed relative to how an average team would perform against the opponent.
        h_off_game = h_goals / (h_avg * a_def)
        h_def_game = a_goals / (a_avg * a_off)
        a_off_game = a_goals / (a_avg * h_def)
        a_def_game = h_goals / (h_avg * h_off)

        # Update stats dicts with data from this game
        stats_dict[h_team]['off'].pop(0)
        stats_dict[h_team]['off'].append(h_off_game)
        stats_dict[h_team]['def'].pop(0)
        stats_dict[h_team]['def'].append(h_def_game)
        stats_dict[h_team]['count'] += 1

        stats_dict[a_team]['off'].pop(0)
        stats_dict[a_team]['off'].append(a_off_game)
        stats_dict[a_team]['def'].pop(0)
        stats_dict[a_team]['def'].append(a_def_game)
        stats_dict[a_team]['count'] += 1
        
        avg_dict['home'].pop(0)
        avg_dict['home'].append(h_goals)
        avg_dict['away'].pop(0)
        avg_dict['away'].append(a_goals)

    return fixtures

def predict_game(h_mean, a_mean):

    # Compile lists of scores for each result
    hWin_scores = [(x, y) for x in range(11) for y in range(11) if x > y]
    draw_scores = [(x, x) for x in range(11)]
    aWin_scores = [(x, y) for x in range(11) for y in range(11) if x < y]

    H_prob = 0.0
    D_prob = 0.0
    A_prob = 0.0

    for score in hWin_scores:
        score_prob = poisson.pmf(score[0], h_mean) * poisson.pmf(score[1], a_mean)
        H_prob += score_prob
    for score in draw_scores:
        score_prob = poisson.pmf(score[0], h_mean) * poisson.pmf(score[1], a_mean)
        D_prob += score_prob
    for score in aWin_scores:
        score_prob = poisson.pmf(score[0], h_mean) * poisson.pmf(score[1], a_mean)
        A_prob += score_prob

    return pd.Series([H_prob, D_prob, A_prob])

def calc_bet(match, marg):

    bet = 'N'
    b = 0.0 # Represents the decimal odds - 1, i.e. the multiplier to calculate profit relative to the bet amount if the bet wins.

    # Check each outcome to see if the margin is exceeded. Place a bet on the outcome with the greatest margin.
    if match['H_prob'] * match['WHH'] > marg:
        bet = 'H'
        marg = match['H_prob'] * match['WHH']
        b = match['WHH'] - 1
        p = match['H_prob']
    if match['D_prob'] * match['WHD'] > marg:
        bet = 'D'
        marg = match['D_prob'] * match['WHD']
        b = match['WHD'] - 1
        p = match['D_prob']
    if match['A_prob'] * match['WHA'] > marg:
        bet = 'A'
        marg = match['A_prob'] * match['WHA']
        b = match['WHA'] - 1
        p = match['A_prob']

    # Calculate Kelly Criterion of the bet
    f = (((b + 1) * p) - 1) / b if b else 0.0
    f = np.maximum(f, 0.0)

    return bet, f, b

def calc_bankroll(fixtures: pd.DataFrame, frac, start_val):

    fixtures['bankroll'] = 0.0
    bankroll = start_val

    for i, row in fixtures.iterrows():
        bet_amount = bankroll * row['f'] / frac
        bet_profit = row['b'] * bet_amount if row['FTR'] == row['bet'] else 0.0 if row['bet'] == 'N' else -bet_amount # Calculate profit (or losses)
        bankroll += bet_profit
        fixtures.at[i, 'bet_amount'] = bet_amount
        fixtures.at[i, 'bet_profit'] = bet_profit
        fixtures.at[i, 'bankroll'] = bankroll
    
    return fixtures