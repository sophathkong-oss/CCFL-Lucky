import pandas as pd

def get_luck_index_v3(league_data):
    '''
    Calculate how 'lucky' a team is based on opponent performance.
    This function calculates the luck index for all teams in the league
    based on the difference between projected and actual scores of their opponents.
    
    Parameters:
    - league_data: The league data containing box scores and team information.
    
    Returns:
    - luck_indices: A list of luck indices for all teams.
    '''
    num_teams = len(league_data['teams'])
    luck_indices = [0] * (num_teams + 5)  # add arbitrary buffer for non-sequential IDs, in case of missing teams

    current_week = league_data['current_week']
    reg_season_count = league_data['regular_season_count']

    # Loop through each regular season week
    for week in range(1, min(current_week + 1, reg_season_count + 1)):
        box_scores = league_data['box_scores'][week]

        # Process each matchup
        for box_score in box_scores:
            # Skip invalid matchups (Bye weeks or incomplete data)
            if box_score['away_team_id'] == 0 or box_score['home_team_id'] == 0:
                continue

            # Update luck index for the home team
            home_team_id = box_score['home_team_id']
            home_luck = box_score['away_projected'] - box_score['away_score']
            if 0 <= home_team_id < len(luck_indices):
                luck_indices[home_team_id] += home_luck

            # Update luck index for the away team
            away_team_id = box_score['away_team_id']
            away_luck = box_score['home_projected'] - box_score['home_score']
            if 0 <= away_team_id < len(luck_indices):
                luck_indices[away_team_id] += away_luck

    return luck_indices

def calculate_pythagorean_expectation_luck(league_data, p=2):
    """
    Calculate Pythagorean Expectation Luck for all teams, with normalization.

    Parameters:
    - league_data: The dictionary with data on teams and matchups.
    - p: The exponent for the Pythagorean formula (default=2).

    Returns:
    - List of dictionaries with Team Name, Team ID, Actual Wins, Expected Wins, and Luck Score.
    """
    team_luck_data = []
    current_week = league_data['current_week']
    games_played = min(current_week - 1, league_data['regular_season_count'])  # Games completed so far

    total_actual_wins = 0
    total_expected_wins = 0

    teams = league_data['teams']

    for team in teams:
        points_for = team['points_for']
        points_against = team['points_against']
        actual_wins = team['wins']

        # Calculate expected win percentage
        expected_win_percentage = (points_for ** p) / ((points_for ** p) + (points_against ** p))

        # Adjust expected wins based on games played so far
        expected_wins = expected_win_percentage * games_played

        # Track totals for normalization
        total_actual_wins += actual_wins
        total_expected_wins += expected_wins

        # Add preliminary team data to the results
        team_luck_data.append({
            "Team Name": team['name'],
            "Team ID": team['id'],
            "Actual Wins": actual_wins,
            "Expected Wins": expected_wins,  # To be normalized
            "Luck Index": None  # Placeholder for now
        })

    # Calculate scaling factor for normalization
    scaling_factor = total_actual_wins / total_expected_wins

    # Normalize expected wins and calculate final luck index
    for team in team_luck_data:
        normalized_expected_wins = team["Expected Wins"] * scaling_factor
        team["Expected Wins"] = round(normalized_expected_wins, 2)
        team["Luck Index"] = round(team["Actual Wins"] - normalized_expected_wins, 2)

    return team_luck_data

def calculate_scatterplot_luck(league_data):
    """
    Calculate matchup-based scatterplot luck for all teams.

    Parameters:
    - league_data: The dictionary with data on teams and matchups.

    Returns:
    - Pandas DataFrame with Team Name, Points For, Points Against, Result, Matchup Luck Type, and Opponent.
    """
    matchup_luck_data = []

    # Preprocess teams for quick lookups
    team_id_to_team = {team["id"]: team for team in league_data["teams"]}

    # Calculate weekly league averages
    weekly_avg_scores = {}
    current_week = league_data['current_week']
    regular_season_count = league_data['regular_season_count']

    for week in range(1, min(current_week, regular_season_count + 1)):
        box_scores = league_data['box_scores'].get(week, [])
        if not box_scores:
            continue

        total_weekly_score = sum(box_score['home_score'] + box_score['away_score'] for box_score in box_scores)
        num_teams = len(box_scores) * 2  # Each matchup involves two teams
        weekly_avg_scores[week] = total_weekly_score / num_teams

    # Iterate through weeks and matchups
    for week in range(1, min(current_week, regular_season_count + 1)):
        box_scores = league_data['box_scores'].get(week, [])  # Safely get box scores for the week
        league_avg_score = weekly_avg_scores.get(week, 0)

        for box_score in box_scores:
            # Skip invalid matchups
            if box_score.get('home_team_id') == 0 or box_score.get('away_team_id') == 0:
                continue

            # Extract match info
            home_score = box_score['home_score']
            away_score = box_score['away_score']
            home_team = team_id_to_team[box_score['home_team_id']]
            away_team = team_id_to_team[box_score['away_team_id']]

            # Normalize scores by league average for Home Team
            home_points_for = home_score - league_avg_score
            home_points_against = away_score - league_avg_score
            home_result = "Win" if home_score > away_score else "Loss"
            home_luck_type = (
                "Lucky Win" if home_result == "Win" and home_points_for < 0 else
                "Unlucky Loss" if home_result == "Loss" and home_points_for > 0 else
                "Neutral"
            )

            matchup_luck_data.append({
                "Week": week,
                "Team Name": home_team["name"],
                "Points For": home_points_for,
                "Points Against": home_points_against,
                "Result": home_result,
                "Matchup Luck Type": home_luck_type,
                "Opponent": away_team["name"]
            })

            # Normalize scores by league average for Away Team
            away_points_for = away_score - league_avg_score
            away_points_against = home_score - league_avg_score
            away_result = "Win" if away_score > home_score else "Loss"
            away_luck_type = (
                "Lucky Win" if away_result == "Win" and away_points_for < 0 else
                "Unlucky Loss" if away_result == "Loss" and away_points_for > 0 else
                "Neutral"
            )

            matchup_luck_data.append({
                "Week": week,
                "Team Name": away_team["name"],
                "Points For": away_points_for,
                "Points Against": away_points_against,
                "Result": away_result,
                "Matchup Luck Type": away_luck_type,
                "Opponent": home_team["name"]
            })

    # Convert the list to a DataFrame
    df = pd.DataFrame(matchup_luck_data)

    return df

def calculate_scheduling_luck(league_data):
    '''
    Simulate hypothetical records for each team based on their matchups and scores.
    This function calculates the hypothetical wins and losses for each team against all other teams
    in the league, excluding their actual matchups.

    Used in scheduling luck analysis.
    '''
    teams = league_data['teams']
    num_weeks = min(league_data['current_week'], league_data['regular_season_count'] + 1)

    # Step 1: Build a dict mapping each team to their weekly scores and opponent IDs
    team_scores_by_week = {team['id']: [] for team in teams}
    opponent_ids_by_week = {team['id']: [] for team in teams}

    for week in range(1, num_weeks):
        for box_score in league_data['box_scores'].get(week, []):
            home_id = box_score['home_team_id']
            away_id = box_score['away_team_id']
            home_score = box_score['home_score']
            away_score = box_score['away_score']

            # Skip invalid matches
            if home_id == 0 or away_id == 0:
                continue

            team_scores_by_week[home_id].append(home_score)
            opponent_ids_by_week[home_id].append(away_id)

            team_scores_by_week[away_id].append(away_score)
            opponent_ids_by_week[away_id].append(home_id)

    # Step 2: Simulate hypothetical records
    hypothetical_records = {
        team['id']: {
            opponent['id']: {'wins': 0, 'losses': 0}
            for opponent in teams
        }
        for team in teams
    }

    for simulated_team in teams:
        sim_id = simulated_team['id']
        sim_scores = team_scores_by_week[sim_id]

        for schedule_donor in teams:
            donor_id = schedule_donor['id']
            donor_opponents = opponent_ids_by_week[donor_id]

            if sim_id == donor_id:
                hypothetical_records[sim_id][donor_id] = {
                    'wins': simulated_team['wins'],
                    'losses': simulated_team['losses']
                }
                continue

            wins = 0
            losses = 0
            for week_index, opponent_id in enumerate(donor_opponents):
                if opponent_id == sim_id:
                    # Skip mirror matchup
                    continue

                opp_score_list = team_scores_by_week.get(opponent_id, [])
                if week_index >= len(sim_scores) or week_index >= len(opp_score_list):
                    continue

                my_score = sim_scores[week_index]
                opp_score = opp_score_list[week_index]

                if my_score > opp_score:
                    wins += 1
                else:
                    losses += 1

            hypothetical_records[sim_id][donor_id]['wins'] = wins
            hypothetical_records[sim_id][donor_id]['losses'] = losses

    return hypothetical_records
