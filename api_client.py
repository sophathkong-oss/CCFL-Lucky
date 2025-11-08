
def fetch_league_data(league):
    """
    Fetch all necessary league data once and store it for reuse.
    """
    data = {
        "league_name": league.settings.name,
        "teams": [{"id": team.team_id, "name": team.team_name, "wins": team.wins, "losses": team.losses, "points_for": team.points_for, "points_against": team.points_against} for team in league.teams],
        "current_week": league.current_week,
        "regular_season_count": league.settings.reg_season_count,
        "box_scores": {}
    }

    # Fetch box scores for each week up to the end of the regular season
    for week in range(1, data["regular_season_count"] + 1):
        try:
            box_scores = league.box_scores(week=week)
            data["box_scores"][week] = []
            for box_score in box_scores:
                # Handle bye weeks where the team is set as the integer 0
                if isinstance(box_score.home_team, int) and box_score.home_team == 0:
                    continue
                if isinstance(box_score.away_team, int) and box_score.away_team == 0:
                    continue

                data["box_scores"][week].append({
                    "home_team_id": box_score.home_team.team_id,
                    "home_score": box_score.home_score,
                    "home_projected": box_score.home_projected,
                    "away_team_id": box_score.away_team.team_id,
                    "away_score": box_score.away_score,
                    "away_projected": box_score.away_projected
                })
        except Exception as e:
            data["box_scores"][week] = None

    return data

