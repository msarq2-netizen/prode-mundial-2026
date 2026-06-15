#!/usr/bin/env python3
"""
Auto-update r.json and live.json with World Cup 2026 results.
Uses football-data.org free API (register at https://www.football-data.org/client/register).
Runs via GitHub Actions every 30 minutes.
"""
import requests
import json
import os
import sys

API_KEY = os.environ.get('FOOTBALL_DATA_KEY', '')

MATCHES = [
    [1,"A","México","Sudáfrica"],
    [2,"A","México","Corea del Sur"],
    [3,"A","México","República Checa"],
    [4,"A","Sudáfrica","Corea del Sur"],
    [5,"A","Sudáfrica","República Checa"],
    [6,"A","Corea del Sur","República Checa"],
    [7,"B","Canadá","Bosnia-Herzegovina"],
    [8,"B","Canadá","Qatar"],
    [9,"B","Canadá","Suiza"],
    [10,"B","Bosnia-Herzegovina","Qatar"],
    [11,"B","Bosnia-Herzegovina","Suiza"],
    [12,"B","Qatar","Suiza"],
    [13,"C","Brasil","Marruecos"],
    [14,"C","Brasil","Haití"],
    [15,"C","Brasil","Escocia"],
    [16,"C","Marruecos","Haití"],
    [17,"C","Marruecos","Escocia"],
    [18,"C","Haití","Escocia"],
    [19,"D","Estados Unidos","Paraguay"],
    [20,"D","Estados Unidos","Australia"],
    [21,"D","Estados Unidos","Turquía"],
    [22,"D","Paraguay","Australia"],
    [23,"D","Paraguay","Turquía"],
    [24,"D","Australia","Turquía"],
    [25,"E","Alemania","Curazao"],
    [26,"E","Alemania","Costa de Marfil"],
    [27,"E","Alemania","Ecuador"],
    [28,"E","Curazao","Costa de Marfil"],
    [29,"E","Curazao","Ecuador"],
    [30,"E","Costa de Marfil","Ecuador"],
    [31,"F","Países Bajos","Japón"],
    [32,"F","Países Bajos","Suecia"],
    [33,"F","Países Bajos","Túnez"],
    [34,"F","Japón","Suecia"],
    [35,"F","Japón","Túnez"],
    [36,"F","Suecia","Túnez"],
    [37,"G","Bélgica","Egipto"],
    [38,"G","Bélgica","Irán"],
    [39,"G","Bélgica","Nueva Zelanda"],
    [40,"G","Egipto","Irán"],
    [41,"G","Egipto","Nueva Zelanda"],
    [42,"G","Irán","Nueva Zelanda"],
    [43,"H","España","Cabo Verde"],
    [44,"H","España","Arabia Saudita"],
    [45,"H","España","Uruguay"],
    [46,"H","Cabo Verde","Arabia Saudita"],
    [47,"H","Cabo Verde","Uruguay"],
    [48,"H","Arabia Saudita","Uruguay"],
    [49,"I","Francia","Senegal"],
    [50,"I","Francia","Irak"],
    [51,"I","Francia","Noruega"],
    [52,"I","Senegal","Irak"],
    [53,"I","Senegal","Noruega"],
    [54,"I","Irak","Noruega"],
    [55,"J","Argentina","Argelia"],
    [56,"J","Argentina","Austria"],
    [57,"J","Argentina","Jordania"],
    [58,"J","Argelia","Austria"],
    [59,"J","Argelia","Jordania"],
    [60,"J","Austria","Jordania"],
    [61,"K","Portugal","Congo DR"],
    [62,"K","Portugal","Uzbekistán"],
    [63,"K","Portugal","Colombia"],
    [64,"K","Congo DR","Uzbekistán"],
    [65,"K","Congo DR","Colombia"],
    [66,"K","Uzbekistán","Colombia"],
    [67,"L","Inglaterra","Croacia"],
    [68,"L","Inglaterra","Ghana"],
    [69,"L","Inglaterra","Panamá"],
    [70,"L","Croacia","Ghana"],
    [71,"L","Croacia","Panamá"],
    [72,"L","Ghana","Panamá"],
]

TEAM_MAP = {
    'Mexico': 'México',
    'South Africa': 'Sudáfrica',
    'South Korea': 'Corea del Sur',
    'Korea Republic': 'Corea del Sur',
    'Czech Republic': 'República Checa',
    'Czechia': 'República Checa',
    'Canada': 'Canadá',
    'Bosnia and Herzegovina': 'Bosnia-Herzegovina',
    'Bosnia-Herzegovina': 'Bosnia-Herzegovina',
    'Qatar': 'Qatar',
    'Switzerland': 'Suiza',
    'Brazil': 'Brasil',
    'Morocco': 'Marruecos',
    'Haiti': 'Haití',
    'Scotland': 'Escocia',
    'USA': 'Estados Unidos',
    'United States': 'Estados Unidos',
    'Paraguay': 'Paraguay',
    'Australia': 'Australia',
    'Turkey': 'Turquía',
    'Türkiye': 'Turquía',
    'Germany': 'Alemania',
    'Curacao': 'Curazao',
    'Curaçao': 'Curazao',
    'Ivory Coast': 'Costa de Marfil',
    "Côte d'Ivoire": 'Costa de Marfil',
    'Ecuador': 'Ecuador',
    'Netherlands': 'Países Bajos',
    'Japan': 'Japón',
    'Sweden': 'Suecia',
    'Tunisia': 'Túnez',
    'Belgium': 'Bélgica',
    'Egypt': 'Egipto',
    'Iran': 'Irán',
    'New Zealand': 'Nueva Zelanda',
    'Spain': 'España',
    'Cape Verde': 'Cabo Verde',
    'Saudi Arabia': 'Arabia Saudita',
    'Uruguay': 'Uruguay',
    'France': 'Francia',
    'Senegal': 'Senegal',
    'Iraq': 'Irak',
    'Norway': 'Noruega',
    'Argentina': 'Argentina',
    'Algeria': 'Argelia',
    'Austria': 'Austria',
    'Jordan': 'Jordania',
    'Portugal': 'Portugal',
    'DR Congo': 'Congo DR',
    'Uzbekistan': 'Uzbekistán',
    'Colombia': 'Colombia',
    'England': 'Inglaterra',
    'Croatia': 'Croacia',
    'Ghana': 'Ghana',
    'Panama': 'Panamá',
}

LIVE_STATUSES = {'IN_PLAY', 'PAUSED'}
DONE_STATUSES = {'FINISHED'}
UPDATE_STATUSES = LIVE_STATUSES | DONE_STATUSES

def normalize(name):
    return TEAM_MAP.get(name, name)

def get_matches():
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {"X-Auth-Token": API_KEY}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    with open('r.json') as f:
        R = json.load(f)

    try:
        with open('live.json') as f:
            old_live = sorted(json.load(f))
    except Exception:
        old_live = []

    print("Fetching World Cup 2026 matches from football-data.org...")
    data = get_matches()
    matches = data.get('matches', [])

    if not matches:
        print(f"No matches returned. Response keys: {list(data.keys())}")
        sys.exit(0)

    print(f"Got {len(matches)} total matches")
    updated = False
    live_matches = []

    for match in matches:
        status = match.get('status', '')
        if status not in UPDATE_STATUSES:
            continue

        home = normalize(match['homeTeam']['name'])
        away = normalize(match['awayTeam']['name'])
        score = match.get('score', {})
        ft = score.get('fullTime', {})
        home_goals = ft.get('home')
        away_goals = ft.get('away')

        if home_goals is None or away_goals is None:
            continue

        for m in MATCHES:
            if m[2] == home and m[3] == away:
                idx = (m[0] - 1) * 2
                if R[idx] != home_goals or R[idx+1] != away_goals:
                    R[idx] = home_goals
                    R[idx+1] = away_goals
                    verb = "LIVE" if status in LIVE_STATUSES else "FT"
                    print(f"  [{verb}] Match {m[0]}: {home} {home_goals}-{away_goals} {away}")
                    updated = True
                if status in LIVE_STATUSES:
                    live_matches.append(m[0])
                break

    live_matches_sorted = sorted(live_matches)
    if live_matches_sorted != old_live:
        with open('live.json', 'w') as f:
            json.dump(live_matches, f)
        print(f"live.json updated: {live_matches}")
        updated = True
    else:
        print(f"live.json unchanged: {live_matches}")

    if updated:
        with open('r.json', 'w') as f:
            json.dump(R, f)
        print("r.json saved.")
    else:
        print("No changes — everything up to date.")
        sys.exit(0)

if __name__ == '__main__':
    main()
