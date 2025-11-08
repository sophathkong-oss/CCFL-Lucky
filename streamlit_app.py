from espn_api.football import League

# For a public league
# league = League(league_id=12345, year=2024)

# For a private league (you need to obtain swid and espn_s2 cookies from your browser)
league = League(league_id=345300502, year=2025, swid="{AC5C036F-7C9B-4076-8342-061D81FE0D76}", espn_s2="AEBQuXNpJN%2FLu6u0QBByjTiNZvHkLoewvgKiIUTE24ine7cD2e8Zi0Qd%2Bi7X0ojBX07TmIdbrat3Nhi9L42BoO%2FxRSYfIwMlsYqhor78Pyjc3Oqm7sJbVcR3pGDlVew32rMIFT7epxJpo12uELAnkUkqY0oxemkx0t%2FvTB7RJtWBHdqw97d4LpVTthPRU%2FYO8clo9V9ZBoBUACYHzXt%2BHmwbfqmSe4%2FCc5jZ%2BfCG97WFtls61x4LPonfRIOkRhqHRw6ZmYS8x90NVy2Hnzbn%2Foa7pqJXDIiUdJLBscB%2FZkOpMA%3D%3D")

# Now you can access various league data and functions, for example:
print(league.settings.name)
print(league.teams)
