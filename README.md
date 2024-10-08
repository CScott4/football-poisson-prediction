# football-poisson-prediction

## Project Description
The aim of this project is to develop a simple prediction method for football (soccer) matches, based on poisson distributions, and test it as a tool for betting.

The model revolves around calculating an offensive and defensive multiplier for each team which represents how they perform in terms of goals scored and goals conceded relative to the average. These multipliers will then be used to calculate two values to be used as the mean values for two poisson distributions representing home goals and away goals for each game. The home poisson mean will be calculated as average home goals * home team offensive multiplier * away team defensive multiplier, and similarly the away mean is average away goals * away team offensive multiplier * home team defensive multiplier.

Multipliers will be calculated as an average of the teams last 19 "performance multipliers". A performance multiplier is how many goals the team scored/conceded relative to the expected mean based on the opponent. For example, the home team's expected goals scored against a paricular opponent will be calculated as average home goals * away team defensive multiplier. If this value comes out as, for example, 1.6, and the home team actually scores 2 goals in the game, then their offensive performance multiplier for that game is 2 / 1.6 = 1.25. I chose to use 19 games because it is equivalent to half a season.
