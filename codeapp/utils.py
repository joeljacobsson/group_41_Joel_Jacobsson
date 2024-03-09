# built-in imports
# standard library imports
import pickle

import pandas as pd
import requests

# external imports
from flask import current_app

# internal imports
from codeapp import db
from codeapp.models import Game


def get_data_list() -> list[Game]:
    """
    Function responsible for downloading the dataset from the source, translating it
    into a list of Python objects, and saving it to a Redis list.
    """

    games: list[Game] = []

    ##### check if dataset already exists, and if so, return the existing dataset  #####
    if db.exists("dataset_list") > 0:  # checks if the `dataset` key already exists
        current_app.logger.info("Dataset already downloaded.")
        dataset_stored: list[Game] = []  # empty list to be returned
        raw_dataset: list[bytes] = db.lrange("dataset_list", 0, -1)  # get list from DB
        for item in raw_dataset:
            dataset_stored.append(pickle.loads(item))  # load item from DB
        return dataset_stored

    search_url: str = "https://onu1.s2.chalmers.se/datasets/IGN_games.csv"
    response = requests.get(search_url, timeout=300)

    with open("IGN_games.csv", "wb") as csv_file:
        csv_file.write(response.content)
        df = pd.read_csv("IGN_games.csv")

        for _, row in df.iterrows():
            new_game = Game(
                title=row["title"],
                score=float(row["score"]),
                score_phrase=row["score_phrase"],
                platform=row["platform"],
                genre=row["genre"],
                release_year=int(row["release_year"]),
                release_month=int(row["release_month"]),
                release_day=int(row["release_day"]),
            )
            db.rpush("dataset_list", pickle.dumps(new_game))
            games.append(new_game)
        return games


def calculate_statistics(dataset: list[Game]) -> dict[str, int]:
    """
    Receives the dataset in the form of a list of Python objects, and calculates the
    number of games per score_phrase on games available on Playstation.

    - filter out games that are available on playstation

    - parameter score_phrase

    - return dict with count of all score_phrases
    """

    score_phrase_count: dict[str, int] = {}
    phrase_order: list[str] = [
        "Masterpiece",
        "Amazing",
        "Great",
        "Good",
        "Okay",
        "Mediocre",
        "Bad",
        "Awful",
        "Painful",
        "Unbearable",
    ]
    for phrase in phrase_order:
        score_phrase_count[phrase] = 0
    for phrase in phrase_order:
        for game in dataset:
            if "playstation" in game.platform.lower():
                if game.score_phrase == phrase:
                    score_phrase_count[phrase] += 1
    return score_phrase_count


def prepare_figure(input_figure: str) -> str:
    """
    Method that removes limits to the width and height of the figure. This method must
    not be changed by the students.
    """
    output_figure = input_figure.replace('height="345.6pt"', "").replace(
        'width="460.8pt"', 'width="100%"'
    )
    return output_figure
