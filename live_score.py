'''
Author: Khizir Siddiqui
Github: khizirsiddiqui
'''

from bs4 import BeautifulSoup
import requests
from plyer import notification
import time

match_list_xml = "http://synd.cricbuzz.com/j2me/1.0/livematches.xml"


def makeSoup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'lxml-xml')
    return soup


def match_data(match):
    data = {}
    data['id'] = match['id']
    data['srs'] = match['srs']
    data['mchDesc'] = match['mchDesc']
    data['type'] = match['type']
    data['mchState'] = match.state['mchState']
    data['status'] = match.state['status']
    return data


def match_commentary(soup, match_id):
    match = soup.find(id=match_id)
    if match is None:
        print("Invalid Match Requested")
        return
    if match.state['mchState'] == 'preview':
        print(match['mchDesc'] + " Match not started yet")
        return
    commentary_url = match['datapath'] + "commentary.xml"
    commentary_xml = makeSoup(commentary_url)
    commentary = commentary_xml.find_all('c')
    mscr = commentary_xml.find('mscr')
    units = []
    for unit in commentary:
        units.append(unit.text)
    batting = {}
    btTm = mscr.find('btTm')
    batting['name'] = btTm['sName']
    batting['runs'] = btTm.find('Inngs')['r']
    batting['overs'] = btTm.find('Inngs')['ovrs']
    batting['wickets'] = btTm.find('Inngs')['wkts']
    btsmn = []
    batsmen = mscr.find_all('btsmn')
    for player in batsmen:
        batsman = {}
        batsman['name'] = player['sName']
        batsman['runs'] = player['r']
        batsman['bowls'] = player['b']
        batsman['fours'] = player['frs']
        batsman['sixes'] = player['sxs']
        # print(batsman['name'] + " " + batsman['runs'])
        btsmn.append(batsman)
    blgTm = mscr.find('blgTm')
    bowling = {}
    bowling['name'] = blgTm['sName']
    if blgTm.find('Inngs') is not None:
        bowling['runs'] = blgTm.find('Inngs')['r']
        bowling['overs'] = blgTm.find('Inngs')['ovrs']
        bowling['wickets'] = blgTm.find('Inngs')['wkts']
    bwlmn = []
    bolwers = mscr.find_all('blrs')
    for player in bolwers:
        bowler = {}
        bowler['name'] = player['sName']
        bowler['runs'] = player['r']
        bowler['overs'] = player['ovrs']
        bowler['wickets'] = player['wkts']
        bwlmn.append(bowler)
    data = {}
    data['match_info'] = match_data(match)
    data['commentary'] = units
    data['batsmen'] = btsmn
    data['bowlers'] = bwlmn
    data['batting'] = batting
    data['bowling'] = bowling
    return data


def match_brief(live_details):
    print(live_details['match_info']['mchDesc'])
    print("   Batting:", end="")
    print(live_details['batting']['name'] + " " + live_details['batting']
          ['runs'] + "/" + live_details['batting']['wickets'])
    for player in live_details['batsmen']:
        print("      " + player['name'] + " " + player['runs'] + "-runs " + player[
              'bowls'] + "-bowls " + player['fours'] + "-4s " + player['sixes'] + "-6s")

    print("   Bowling:", end="")
    print(live_details['bowling']['name'])
    for bowler in live_details['bowlers']:
        print("      " + bowler['name'] + " " +
              bowler['wickets'] + "-" + bowler['runs'])
    print("   Recent:")
    print("      " + live_details['commentary'][0])


def match_msg(live_details):
    alpha = live_details['batting']['name'] + " " + live_details[
        'batting']['runs'] + "/" + live_details['batting']['wickets']
    beta = live_details['commentary'][0]
    return alpha + "\n" + beta


def match_list(soup):
    matches = soup.find_all('match')
    list = []
    for match in matches:
        list.append(match_data(match))
    return list

soup = makeSoup(match_list_xml)
matches = match_list(soup)
while True:
    for idx, match in enumerate(matches):
        mid = match['id']
        live_details = match_commentary(soup, mid)
        if live_details is not None and idx == 0: # remove idx condition to see all matches
            print(str(idx + 1), end='. ')
            match_brief(live_details)
            notification.notify(
                title=live_details['match_info']['mchDesc'],
                message=match_msg(live_details),
                app_name='IPL-2017 Score',
                app_icon='ipl.ico',
                timeout=10,
            )
        print()
        time.sleep(10)
