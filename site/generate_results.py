import pandas as pd
import gspread

gc = gspread.service_account(filename='serviceaccount.json')

gsheets = gc.open_by_url('[redacted]')

out_string = """
# Results

[home](index.md) | [rules](rules.md) | [stages and rallies](stages.md) | [results and standings](results.md) | [teams](teams.md)

"""

comments = [
'',
'',
'','','','','',
]

## read stuff
rallies = ['norway', 'sardinia', 'japan', 'kenya', 'germany', 'finland', 'indonesia']

points_ladder = [25, 20, 16, 14, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

ps_ladder = [4,3,2,1]

def rally_points(pos):
    if pos <= len(points_ladder):
        return points_ladder[round(pos) - 1]
    else:
        return 0

def ps_points(pos):
    if pos <= len(ps_ladder):
        return ps_ladder[round(pos) - 1]
    else:
        return 0

sheets = gsheets.worksheet('teams').get_all_values()

team_df = pd.DataFrame(sheets[0:], columns=sheets[0]).query('team != " "')

team_df = team_df[['name', 'team']]


# here it happens

standings = 0
team_standings = 0
n=0

for rally in rallies:

    sheets = gsheets.worksheet(rally).get_all_values()
    df = pd.DataFrame(sheets[3:], columns=sheets[2]).query('rank != ""')

    results = df[['name', 'min time', 'power stage', 'max penalty', 'link']]
    results.columns = ['name', 'time', 'powerstage', 'penalty', 'link']

    results['link'] = results.link.apply(lambda x: f"[link]({x})")

    results = results.merge(team_df, on='name', how='left').fillna("")

    results['pos'] = results['time'].rank()
    results['pspos'] = results['powerstage'].rank()
    results['rally'] = results.pos.apply(rally_points).astype(int)
    results['ps'] = results.pspos.apply(ps_points).astype(int)
    results['points'] = (results.rally + results.ps).astype(int)

    results = results[['pos', 'name', 'time', 'powerstage', 'rally', 'ps', 'points', 'team', 'penalty', 'link',]]

    out_string += '\n\n' + '## ' + rally
    out_string += '\n\n' + comments[n]
    out_string += '\n\n' + results.to_markdown(index=False)

    if type(standings) == int:
        standings = results[['name', 'points']].rename(columns={'points': rally})
        standings = standings.fillna(0)
        standings[rally] = standings[rally].astype(int)
    else:
        standings = standings.merge(
            results.rename(columns={'points': rally})[['name', rally]],
            on='name',
            how='outer'
        ).fillna(0)
        standings[rally] = standings[rally].astype(int)

    team_results = results.copy(deep=False).query('team > ""')
    team_results['rank_in_team'] = team_results.groupby("team")['pos'].rank(ascending=True, method='dense')
    team_results['ps_in_team'] = team_results.groupby("team")['powerstage'].rank(ascending=True, method='dense')
    team_results = team_results.query('rank_in_team <= 3')
    team_results['rank_filtered'] = team_results.pos.rank(ascending=True, method='dense')
    team_results['team_points'] = team_results.rank_filtered.apply(rally_points)
    team_results = team_results[['team', 'team_points']].groupby('team').sum().astype(int).reset_index()

    if type(team_standings) == int:
        team_standings = team_results[['team', 'team_points']].rename(columns={'team_points': rally})
    else:
        team_standings = team_standings.merge(
            team_results.rename(columns={'team_points': rally})[['team', rally]],
            on='team',
            how='outer'
        ).fillna(0)

    n += 1


team_standings['total'] = team_standings[rallies].fillna(0).sum(axis=1)
team_standings = team_standings.sort_values(by='total', ascending=False)

standings['total'] = standings[rallies].fillna(0).sum(axis=1) - standings[rallies].fillna(0).min(axis=1)
standings['best_result'] = standings[rallies].fillna(0).max(axis=1)

standings = standings.sort_values(by=['total', 'best_result'], ascending=False)
standings = standings.drop(columns='best_result')

#standings.to_markdown('results/' + 'standings.md', index=False)
out_string += '\n\n' + "## standings"
out_string += '\n\n' + standings.fillna('-').to_markdown(index=False)

out_string += '\n\n' + "## team standings"
out_string += '\n\n' + team_standings.to_markdown(index=False)


# write output

output_file = open('results.md','w')
output_file.write(out_string)
output_file.close()
