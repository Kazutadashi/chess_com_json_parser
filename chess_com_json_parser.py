#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is a JSON parser for information regarding titled players on Chess.com. It collects various
rating statistics, and scores for tactics, and puzzle rush. It also collects location data when available.
"""

__author__ = "Owen LaReaux"
__version__ = "1.0"
__maintainer__ = "Owen LaReaux"
__email__ = "owen.lareaux@utah.edu"


import json
import pandas as pd
import urllib.request
import time


FIDE_TITLES = ("GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM")
FEATURES = ("rapid_rating", "rapid_wins", "rapid_losses", "rapid_draws",
            "blitz_rating", "blitz_wins", "blitz_losses", "blitz_draws",
            "bullet_rating", "bullet_wins", "bullet_losses", "bullet_draws",
            "tactics_rating", "puzzle_rush_rating", "country", "location", "title")


def get_list_of_titled_players(title):
    """
    Downloads a list of players with specified title on Chess.com
    :param title:           The desired title to use for getting player list
    :return list_of_users:  Returns the list of all users with this title on Chess.com
    """
    try:
        print("Fetching JSON data from server...")
        with urllib.request.urlopen("https://api.chess.com/pub/titled/" + title) as url:
            list_of_users = json.loads(url.read().decode())

    except Exception as exception:
        print(exception)

    return list_of_users['players']


def compute_stats(player):
    """
    Collects all information about a specific player's stats
    :param player:  The name of the player
    :return:        Returns all available stats
    """
    try:
        print("Getting player data for " + player + "...")
        with urllib.request.urlopen("https://api.chess.com/pub/player/" + player + "/stats") as url:
            player_data = json.loads(url.read().decode())

    except Exception as exception:
        print(exception)

    return player_data

def get_other_data(player):
    """
    Collects location and fide title information for given player. Note that the location data is
    user user, and can be nonsensical at times.

    If a location is not found, it replaces it with "No Location Data Available".

    :param player:  The name of the player
    :return:        Returns country and location (Salt Lake City, Utah for example)
    """
    try:
        #print("Getting location data for " + player + "...")
        with urllib.request.urlopen("https://api.chess.com/pub/player/" + player) as url:
            location_data = json.loads(url.read().decode())

    except Exception as exception:
        print(exception)

    country  = location_data['country'].replace("https://api.chess.com/pub/country/", '')

    try:
        location = location_data['location']
    except KeyError:
        location = 'No Location Data Available'

    try:
        title = location_data['title']
    except KeyError:
        title = 'None'
    return [country, location, title]


def get_relevant_information(player):
    """
    Gets rating informationfor rapid, blitz, and bullet, as well as the win/loss/draw counts. Also gets
    available data for tactics and puzzle rush. Note that puzzle rush is divided into 3 categories:
    3 min, 5 min, and survival. Unfortunately Chess.com only provides the highest score regardless of category
    so there is no way to know which category it came from :(

    If it is unable to find a rating, we assign it a rating of 0.

    :param player: Username of player
    :return: returns a list of all the data collected
    """
    player_stats = compute_stats(player)
    # --------- Rapid Stats --------- #
    try:
        rapid_rating = str(player_stats['chess_rapid']['best']['rating'])
    except KeyError:
        rapid_rating = "0"

    try:
        rapid_wins = str(player_stats['chess_rapid']['record']['win'])
    except KeyError:
        rapid_wins = "0"

    try:
        rapid_losses = str(player_stats['chess_rapid']['record']['loss'])
    except KeyError:
        rapid_losses = "0"

    try:
        rapid_draws = str(player_stats['chess_rapid']['record']['draw'])
    except KeyError:
        rapid_draws = "0"

    # --------- Blitz Stats --------- #
    try:
        blitz_rating = str(player_stats['chess_blitz']['best']['rating'])
    except KeyError:
        blitz_rating = "0"

    try:
        blitz_wins = str(player_stats['chess_blitz']['record']['win'])
    except KeyError:
        blitz_wins = "0"

    try:
        blitz_losses = str(player_stats['chess_blitz']['record']['loss'])
    except KeyError:
        blitz_losses = "0"

    try:
        blitz_draws = str(player_stats['chess_blitz']['record']['draw'])
    except KeyError:
        blitz_draws = "0"

    # --------- Bullet Stats --------- #
    try:
        bullet_rating = str(player_stats['chess_bullet']['best']['rating'])
    except KeyError:
        bullet_rating = "0"

    try:
        bullet_wins = str(player_stats['chess_bullet']['record']['win'])
    except KeyError:
        bullet_wins = "0"

    try:
        bullet_losses = str(player_stats['chess_bullet']['record']['loss'])
    except KeyError:
        bullet_losses = "0"

    try:
        bullet_draws = str(player_stats['chess_bullet']['record']['draw'])
    except KeyError:
        bullet_draws = "0"

    # --------- Tactics Stats --------- #
    try:
        tactics_rating = str(player_stats['tactics']['highest']['rating'])
    except KeyError:
        tactics_rating = "0"

    # --------- Puzzle Rush Stats --------- #
    try:
        # Note that this only shows the best score of all three categories unfortunately
        puzzle_rush_rating = str(player_stats['puzzle_rush']['best']['score'])
    except KeyError:
        puzzle_rush_rating = "0"

    # --------- Location Stats --------- #
    try:
        pass
    except:
        pass
    return [rapid_rating, rapid_wins, rapid_losses, rapid_draws,
            blitz_rating, blitz_wins, blitz_losses, blitz_draws,
            bullet_rating, bullet_wins, bullet_losses, bullet_draws,
            tactics_rating, puzzle_rush_rating]


def create_entry(player):
    """
    Creates a list containing all relevant information on this player to be used in the dataframe later
    :param player: Player's username
    :return: List of rapid, blitz, bullet, tactics, puzzle rush, country, location, and fide title info.
    """
    return get_relevant_information(player) + get_other_data(player)


def create_data_frame(fide_titles):
    """
    Creates a data frame which is used to create a CSV file for use in later data analysis. Creates several CSV files
    containing information for all players with that title.
    :param fide_titles: A list of FIDE titles
    :return: None
    """
    current_dict = dict()

    for title in fide_titles:
        print("Creating CSV file for " + title + " players.")
        t0 = time.time()

        # Creating row for each player to add to the dataframe.
        for player in get_list_of_titled_players(title):
            current_dict[player] = create_entry(player)

        final_data_frame = pd.DataFrame.from_dict(current_dict, orient='index')
        final_data_frame.columns = FEATURES
        final_data_frame.to_csv(path_or_buf='chess_data_' + title + '.csv', index=True, encoding='utf-8',
                                index_label='player_name')

        t1 = time.time()
        print("Time it took to finish: " + str(t1 - t0) + " seconds.")
        print("Done creating CSV. Going to next FIDE title.")

    return None

create_data_frame(FIDE_TITLES)









