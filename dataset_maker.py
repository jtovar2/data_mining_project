import sqlite3
import numpy
from random import randint

database = 'database.sqlite'
conn = sqlite3.connect(database)

sql_query = "SELECT * FROM Match;"

get_match_query = "SELECT date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal from Match where id = {match_id}"

get_team_attributes_alternate_query = '''SELECT buildUpPlaySpeed, buildUpPlayPassing, chanceCreationPassing,
chanceCreationCrossing, chanceCreationShooting, defencePressure, defenceAggression
FROM Team_Attributes 
WHERE date >= '{match_date}' and team_api_id = {team_id}
ORDER BY date ASC LIMIT 1'''

get_team_attributes_query = '''SELECT buildUpPlaySpeed, buildUpPlayPassing, chanceCreationPassing,
chanceCreationCrossing, chanceCreationShooting, defencePressure, defenceAggression
FROM Team_Attributes 
WHERE date <= '{match_date}' and team_api_id = {team_id}
ORDER BY date DESC LIMIT 1'''



'''Returns the percentage of the last five matches. So if 100 won all 15 points possible of the last five'''
def get_last_five_matches_rating(team_id, match_date):
    get_last_5_matches_query = '''SELECT home_team_api_id, away_team_api_id, home_team_goal, away_team_goal from Match where (home_team_api_id = {team_id} or away_team_api_id = {team_id}) and date < '{match_date}' Order by date DESC LIMIT 5'''
    cursor = conn.execute(get_last_5_matches_query.format(match_date=match_date, team_id=team_id))
    results = cursor.fetchall()
    points_earned = 0.0
    for row in results:
        if row[2] == row[3]:
            points_earned = points_earned + 1
        elif row[0] == team_id:
            if row[2] > row[3]:
                points_earned = points_earned + 3
        else:
            if row[3] > row[2]:
                points_earned = points_earned + 3
    max_points_earned = len(results)*3
    if max_points_earned == 0:
        return 0

    return float(points_earned/max_points_earned)

def get_last_five_matches_with_role_rating(team_id, match_date, role):
    if role == 'home':
        get_last_5_matches_at_home_query = '''SELECT home_team_goal, away_team_goal from Match where home_team_api_id = {team_id} and date < '{match_date}' order by date DESC LIMIT 5 '''
        cursor = conn.execute(get_last_5_matches_at_home_query.format(team_id=team_id, match_date=match_date))
        results = cursor.fetchall()
        pts_earned = 0.0
        for row in results:
            if row[0] == row[1]:
                pts_earned = pts_earned + 1
            elif row[0] > row[1]:
                pts_earned = pts_earned + 3
        max_points_earned = len(results) * 3
        if max_points_earned == 0:
            return None
        return float(pts_earned/max_points_earned)
    else:
        get_last_5_matches_away_query = '''SELECT home_team_goal, away_team_goal from Match where away_team_api_id = {team_id} and date < '{match_date}' order by date DESC LIMIT 5 '''
        cursor = conn.execute(get_last_5_matches_away_query.format(team_id=team_id, match_date=match_date))
        results = cursor.fetchall()
        pts_earned = 0.0
        for row in results:
            if row[0] == row[1]:
                pts_earned = pts_earned + 1
            elif row[1] > row[0]:
                pts_earned = pts_earned + 3
        max_points_earned = len(results) * 3
        if max_points_earned == 0:
            return None
        return float(pts_earned/max_points_earned)


def get_match_data(match_id):
    query = get_match_query.format(match_id=match_id)
    cursor = conn.execute(query)
    result = cursor.fetchall()
    return result[0]

def get_team_attributes(team_id, match_date, role):
    query = get_team_attributes_query.format(match_date=match_date, team_id=team_id)
    cursor = conn.execute(query)
    result = cursor.fetchall()
    if len(result) == 0:
        cursor = conn.execute(get_team_attributes_alternate_query.format(match_date=match_date, team_id=team_id))
        result = cursor.fetchall()
    last_5_matches_rating = get_last_five_matches_rating(team_id, match_date)
    last_5_matches_with_role_rating = get_last_five_matches_with_role_rating(team_id, match_date, role)
    if len(result) == 0 or last_5_matches_rating is None or last_5_matches_with_role_rating is None:
        return None
    decimal_team_attributes = []
    for number in result[0]:
        decimal_team_attributes.append(float(number/100.0))
    return tuple(decimal_team_attributes) + (last_5_matches_rating, last_5_matches_with_role_rating)

def make_matrix_row(match_result, home_team_tuple, away_team_tuple):
    matrix_row = home_team_tuple + away_team_tuple + (match_result,)

    return matrix_row



def generate_text_file(text_file_name, number_of_matches):
    random_match_ids_training = [randint(1,24000) for p in range(0,number_of_matches)]
    list_of_match_tuples = []
    count = 0

    for match in random_match_ids_training:
        match_data = get_match_data(match)
        match_date = match_data[0]
        home_team = match_data[1]
        away_team = match_data[2]
        home_team_data = get_team_attributes(home_team, match_date, 'home')
        away_team_data = get_team_attributes(away_team, match_date, 'away')
        match_result = 1.0
        if match_data[3] == match_data[4]:
            match_result = 0.5
        elif match_data[3] < match_data[4]:
            match_result = 0.0
        if away_team_data is not None and home_team_data is not None:
            matrix_row = make_matrix_row(match_result, home_team_data, away_team_data)
            list_of_match_tuples.append(matrix_row)
        print count
        count = count + 1

    numpy_matches = numpy.asarray(list_of_match_tuples)
    numpy.savetxt(text_file_name, numpy_matches)
    print "done"


generate_text_file("testing_set.txt", 500)

