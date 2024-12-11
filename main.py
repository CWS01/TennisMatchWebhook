from discord_webhook import DiscordWebhook
import requests
from datetime import datetime
from time import sleep

TODAY = datetime.now()
DATE = TODAY.date()

API_KEY = "9pvkxsnk69acdcgbgeubd8c8"
REQUESTS_URI = "http://api.sportradar.us/tennis/trial/v3/en/schedules/live/summaries.json?api_key=9pvkxsnk69acdcgbgeubd8c8"
DAILY_SUMMARIES = f"https://api.sportradar.com/tennis/trial/v3/en/schedules/{DATE}/summaries.json?api_key=9pvkxsnk69acdcgbgeubd8c8"

headers = {
    
}

# Three requests are made to ensure that every match in a given day is returned from the API as they API only allows for
# a limit of 200
parameters = {
    "start": 10,
    "limit": 200
}

response = requests.get(url=DAILY_SUMMARIES, headers=headers, params=parameters)
# print(response.raise_for_status())
data = response.json()["summaries"]
# pprint(data)
sleep(5)
parameters = {
    "start": 211,
    "limit": 200
}

response = requests.get(url=DAILY_SUMMARIES, headers=headers, params=parameters)
# print(response.raise_for_status())
data2 = response.json()["summaries"]
for index in range(len(data2)):
    data.append(data2[index])

sleep(5)
parameters = {
    "start": 411,
    "limit": 200
}

response = requests.get(url=DAILY_SUMMARIES, headers=headers, params=parameters)
# print(response.raise_for_status())
data3 = response.json()["summaries"]
for index in range(len(data3)):
    data.append(data3[index])

# For loop that extract the player information for each of the matches
matches = []
player1 = []
player2 = []
player1_countries = []
player2_countries = []
for event in data:
    match = (event['sport_event']['competitors'])
    if (event['sport_event']['sport_event_context']['competition']['type'] == 'singles' and
            (event['sport_event']['sport_event_context']['category']['name'] == "ATP" or
             event['sport_event']['sport_event_context']['category']['name'] == "WTA")):
        if '/' not in match[0]['name']:
            competitor1 = match[0]['name']
            competitor2 = match[1]['name']
            player1.append(competitor1)
            player2.append(competitor2)

            try:
                player1_country = match[0]['country']
                player2_country = match[1]['country']
                player1_countries.append(player1_country)
                player2_countries.append(player2_country)
            except KeyError:
                player1_countries.append("No Country Found")

# For loop to extract the match level (i.e. ATP), the tournament the match is a part of, the tournament level (i.e. ATP 500),
# the round of each match, the start time for each match, and the court each match is being played on
match_level = []
tournament = []
tournament_level = []
rounds = []
start_times = []
courts = []
for event in data:
    if (event['sport_event']['sport_event_context']['competition']['type'] == 'singles' and
            (event['sport_event']['sport_event_context']['category']['name'] == "ATP" or
             event['sport_event']['sport_event_context']['category']['name'] == "WTA")):
        tournament.append(event['sport_event']['sport_event_context']['competition']['name'])
        match_level.append(event['sport_event']['sport_event_context']['category']['name'])
        rounds.append(event['sport_event']['sport_event_context']['round']['name'])
        start_times.append(event['sport_event']['start_time'])
        try:
            courts.append(event["sport_event"]["venue"]["name"])
        except KeyError:
            courts.append("No Court Listed")
        try:
            tournament_level.append(event['sport_event']['sport_event_context']['competition']['level'])
        except KeyError:
            print("Not an ATP or WTA tournament")

# For loop that formats the court that each match is being played on
formatted_courts = []
for court in courts:
    if "Quadra" in court:
        new_name = court.replace("Quadra", "Court")
        formatted_courts.append(new_name)
    else:
        formatted_courts.append(court)

# For loop to format all the starting times in EST
formatted_start_times = []
for time in start_times:
    new_time = time.split("T")[1]
    new_time = new_time.split("+")[0]
    time_split = new_time.split(":")
    hours_place = int(time_split[0])
    est_time = hours_place - 5
    if est_time < 0 and int(time_split[1]) <= 59:
        if int(time_split[1]) > 0 and abs(est_time) >= 2:
            formatted_time = f"{est_time + 23}:{time_split[1]}:{time_split[2]} (Last Night)"
            formatted_start_times.append(formatted_time)
        elif int(time_split[1]) > 0 and abs(est_time) < 2:
            formatted_time = f"{est_time + 23}:{time_split[1]}:{time_split[2]} (Last Night)"
            formatted_start_times.append(formatted_time)
        elif abs(est_time) < 2:
            formatted_time = f"{est_time + 24}:{time_split[1]}:{time_split[2]} (Last Night)"
            formatted_start_times.append(formatted_time)
        else:
            formatted_time = f"{est_time + 24}:{time_split[1]}:{time_split[2]} (Last Night)"
            formatted_start_times.append(formatted_time)
    elif est_time < 10:
        formatted_time = f"0{est_time}:{time_split[1]}:{time_split[2]}"
        formatted_start_times.append(formatted_time)
    else:
        formatted_time = f"{est_time}:{time_split[1]}:{time_split[2]}"
        formatted_start_times.append(formatted_time)

# Formats the le
formatted_tournament_level = []
for level in tournament_level:
    new_level = level.replace("_", " ")
    formatted_tournament_level.append(new_level.upper())

formatted_rounds = []
for round in rounds:
    new_round = round.replace("_", " ")
    formatted_rounds.append(new_round.title())


webhook = DiscordWebhook(
    url="https://discord.com/api/webhooks/1207513917643825193/sU3cBn8y3xdLbIMu1nYeAly9hKHQvkVmOQ7_rEWMNo3DST9ucdZCOKmaauzfkPeYa_Jg")

webhook.set_content("--------------------------------------------")
webhook.execute()
webhook.set_content("## ***__Today's ATP Matches:__***")
webhook.execute()
n = 1
for i in range(len(player1)):
    sleep(1)
    if match_level[i] == "ATP":
        webhook.set_content(
            f"{n}) **Matchup: {player1[i]} ({player1_countries[i]}) vs. {player2[i]} ({player2_countries[i]}) ({formatted_tournament_level[i]})**\n"
            f"*Tournament: {tournament[i]}*\n"
            f"Stage: {formatted_rounds[i]}\n"
            f"Start Time (24 Hour): {formatted_start_times[i]} EST\n"
            f"Court: {formatted_courts[i]}",
            )
        response = webhook.execute()
        n += 1

webhook.set_content("--------------------------------------------")
webhook.execute()
webhook.set_content("## ***__Today's WTA Matches:__***")
webhook.execute()
m = 1
for i in range(len(player1)):
    sleep(1)
    if match_level[i] == "WTA":
        webhook.set_content(
            f"{m}) **Matchup: {player1[i]} ({player1_countries[i]}) vs. {player2[i]} ({player2_countries[i]}) ({formatted_tournament_level[i]})**\n"
            f"*Tournament: {tournament[i]}*\n"
            f"Stage: {formatted_rounds[i]}\n"
            f"Start Time (24 Hour): {formatted_start_times[i]} EST\n"
            f"Court: {formatted_courts[i]}",
            )
        response = webhook.execute()
        m += 1
