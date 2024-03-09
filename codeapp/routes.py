# pylint: disable=cyclic-import
"""
File that contains all the routes of the application.
This is equivalent to the "controller" part in a model-view-controller architecture.
In the final project, you will need to modify this file to implement your project.
"""
# built-in imports
import io

# external imports
from flask import Blueprint, jsonify, render_template
from flask.wrappers import Response as FlaskResponse
from matplotlib.figure import Figure
from werkzeug.wrappers.response import Response as WerkzeugResponse

# internal imports
from codeapp.models import Game
from codeapp.utils import calculate_statistics, get_data_list, prepare_figure

# define the response type
Response = str | FlaskResponse | WerkzeugResponse

bp = Blueprint("bp", __name__, url_prefix="/")


################################### web page routes ####################################


@bp.get("/")  # root route
def home() -> Response:
    # gets dataset
    dataset: list[Game] = get_data_list()

    # get the statistics that is supposed to be shown
    counter: dict[str, int] = calculate_statistics(dataset)

    # render the page
    return render_template("home.html", counter=counter)


@bp.get("/image")
def image() -> Response:
    # gets dataset
    dataset: list[Game] = get_data_list()
    # get the statistics that is supposed to be shown
    counter: dict[str, int] = calculate_statistics(dataset)

    # creating the plot
    fig = Figure()
    fig.gca().bar(
        list(counter.keys()),
        list(counter.values()),
        color="gray",
        alpha=0.5,
        zorder=2,
    )
    fig.gca().plot(
        list(counter.keys()),
        list(counter.values()),
        marker="x",
        color="#25a848",
        zorder=3,
    )
    fig.gca().grid(ls=":", zorder=1)
    fig.gca().set_xticks(range(len(counter.items())))
    fig.gca().set_xticklabels(counter.keys(), rotation=-45, ha="left")
    fig.gca().set_xlabel("Score Phrase")
    fig.gca().set_ylabel("Number of Games")
    fig.tight_layout()

    ################ START -  THIS PART MUST NOT BE CHANGED BY STUDENTS ################
    # create a string buffer to hold the final code for the plot
    output = io.StringIO()
    fig.savefig(output, format="svg")
    # output.seek(0)
    final_figure = prepare_figure(output.getvalue())
    return FlaskResponse(final_figure, mimetype="image/svg+xml")


@bp.get("/about")
def about() -> Response:
    return render_template("about.html")


################################## web service routes ##################################


@bp.get("/json-dataset")
def get_json_dataset() -> Response:
    # gets dataset
    dataset: list[Game] = get_data_list()

    # render the page
    return jsonify(dataset)


@bp.get("/json-stats")
def get_json_stats() -> Response:
    # gets dataset
    dataset: list[Game] = get_data_list()

    # get the statistics that is supposed to be shown
    games: dict[str, int] = calculate_statistics(dataset)

    # render the page
    return jsonify(games)
