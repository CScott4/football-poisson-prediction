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
leagues = ['E0'] 

E_df = pd.DataFrame()

for year in years:
    for league in leagues:
        response = requests.get(f'{base_url}{year}/{league}.csv')

        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            
            df = pd.read_csv(csv_data, on_bad_lines='skip')
            df['season'] = year

            E_df = pd.concat([E_df, df])

# Deal with differences in data across different years
E_df['Div'].fillna(E_df['ï»¿Div'], inplace=True)

# Getting rid of the columns I'm not interested in. I will use William Hill for the odds as that is the only bookmaker we have data for over all seasons
E_df.drop(columns=['Attendance', 'Referee', 'HC', 'AC', 'HF', 'AF', 'HO', 'AO', 'HY', 'AY', 'HR', 'AR', 'HBP', 'ABP', 'GBH', 'GBD', 'GBA', 
                   'IWH', 'IWD', 'IWA', 'LBH', 'LBD', 'LBA', 'SBH', 'SBD', 'SBA', 'SYH', 'SYD', 'SYA', 'SOH', 'SOD', 'SOA', 
                   'GB>2.5', 'GB<2.5', 'B365>2.5', 'B365<2.5', 'Unnamed: 48', 'Unnamed: 49','Unnamed: 50', 'Unnamed: 51', 'Unnamed: 52', 
                   'GBAHH', 'GBAHA', 'GBAH', 'LBAHH', 'LBAHA', 'LBAH', 'B365AHH', 'B365AHA', 'B365AH', 'BWH', 'BWD', 'BWA', 'SJH', 'SJD', 'SJA', 
                   'VCH', 'VCD', 'VCA', 'Bb1X2', 'BbMxH', 'BbAvH', 'BbMxD', 'BbAvD', 'BbMxA', 'BbAvA', 'BbOU', 'BbMx>2.5', 'BbAv>2.5', 'BbMx<2.5', 'BbAv<2.5', 
                   'BbAH', 'BbAHh', 'BbMxAHH', 'BbAvAHH', 'BbMxAHA', 'BbAvAHA', 'BSH', 'BSD', 'BSA', 'PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA', 
                   'Time', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA', 'P>2.5', 'P<2.5', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5', 
                   'AHh', 'PAHH', 'PAHA', 'MaxAHH', 'MaxAHA', 'AvgAHH', 'AvgAHA', 'B365CH', 'B365CD', 'B365CA', 'BWCH', 'BWCD', 'BWCA', 
                   'IWCH', 'IWCD', 'IWCA', 'WHCH', 'WHCD', 'WHCA', 'VCCH', 'VCCD', 'VCCA', 'MaxCH', 'MaxCD', 'MaxCA', 'AvgCH', 'AvgCD', 'AvgCA', 
                   'B365C>2.5', 'B365C<2.5', 'PC>2.5', 'PC<2.5', 'MaxC>2.5', 'MaxC<2.5', 'AvgC>2.5', 'AvgC<2.5', 'AHCh', 'B365CAHH', 'B365CAHA', 
                   'PCAHH', 'PCAHA', 'MaxCAHH', 'MaxCAHA', 'AvgCAHH', 'AvgCAHA', 'ï»¿Div', 'BFH', 'BFD', 'BFA', '1XBH', '1XBD', '1XBA', 
                   'BFEH', 'BFED', 'BFEA', 'BFE>2.5', 'BFE<2.5', 'BFEAHH', 'BFEAHA', 'BFCH', 'BFCD', 'BFCA', '1XBCH', '1XBCD', '1XBCA', 
                   'BFECH', 'BFECD', 'BFECA', 'BFEC>2.5', 'BFEC<2.5', 'BFECAHH', 'BFECAHA','B365H', 'B365D', 'B365A', 'HHW', 'AHW', 
                   'HTHG', 'HTAG', 'HTR', 'HS', 'AS', 'HST', 'AST'], inplace=True)

E_df.dropna(inplace=True)

E_df['Date'] = pd.to_datetime(E_df['Date'], dayfirst=True)

E_df.reset_index(drop=True, inplace=True)

E_df['FTHG'] = E_df['FTHG'].astype(int)
E_df['FTAG'] = E_df['FTAG'].astype(int)

# Save to pickle
E_df.to_pickle('EPL_00-01_to_24-25.pkl')