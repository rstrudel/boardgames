import os
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors

from boardgames import utils


class Codenames:
    def __init__(self):
        self.n_side = 5
        self.n_words = self.n_side ** 2

        self.idx_to_type = {-1: "hidden", 0: "blue", 1: "red", 2: "neutral", 3: "lose"}
        self.type_to_idx = {v: k for k, v in self.idx_to_type.items()}
        self.type_en_to_fr = {
            "blue": "bleue",
            "red": "rouge",
            "neutral": "neutre",
            "lose": "défaite",
        }
        with open(os.path.join(os.path.dirname(__file__), "words.txt"), "r") as f:
            self.every_word = f.read().split("\n")

    def reset(self):
        """
        Start a new game and return a red_starting boolean
        """
        idx_words = np.random.permutation(np.arange(len(self.every_word)))[
            : self.n_words
        ]
        idx_words = idx_words.reshape((5, 5))

        # picking words
        self.words = np.zeros((self.n_side, self.n_side)).astype("U256")
        self.formatted_words = np.zeros((self.n_side, self.n_side)).astype("U256")
        for i in range(self.n_side):
            for j in range(self.n_side):
                self.words[i, j] = self.every_word[idx_words[i, j]]
                self.formatted_words[i, j] = utils.format_str(self.words[i, j])

        # spy grid definition
        red_starting = np.random.randint(2)
        blue_tokens = 8 + 1 - red_starting
        red_tokens = 8 + red_starting
        # initialize spy_grid with neutral squares
        spy_grid = self.type_to_idx["neutral"] * np.ones(self.n_words)
        spy_grid[:blue_tokens] = self.type_to_idx["blue"]
        spy_grid[blue_tokens : blue_tokens + red_tokens] = self.type_to_idx["red"]
        spy_grid[blue_tokens + red_tokens] = self.type_to_idx["lose"]
        spy_grid = np.random.permutation(spy_grid).reshape(self.n_side, self.n_side)

        self.blue_tokens = blue_tokens
        self.red_tokens = red_tokens
        self.spy_grid = spy_grid

        self.played_squares = -np.ones((self.n_side, self.n_side))
        self.red_playing = red_starting

    def save_grid(self, path, grid):
        fig, ax = plt.subplots()  # figsize=figsize)

        # make a color map of fixed colors
        cmap = colors.ListedColormap(["white", "blue", "red", "yellow", "black"])
        bounds = [-1, 0, 1, 2, 3, 4]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        # tell imshow about color map so that only set colors are used
        for i in range(self.n_side):
            for j in range(self.n_side):
                color = "black"
                # as blue or end game squares are dark, set color to white
                if self.idx_to_type[grid[j, i]] in ["lose"]:
                    color = "white"
                ax.text(
                    i + 0.5,
                    (self.n_side - 1 - j) + 0.5,
                    self.words[j, i],
                    horizontalalignment="center",
                    verticalalignment="center",
                    color=color,
                )
        ax.imshow(
            grid[::-1, :],
            interpolation="nearest",
            origin="lower",
            cmap=cmap,
            norm=norm,
            extent=[0, self.n_side, 0, self.n_side],
        )
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(True)
        fig.savefig(path, bbox_inches="tight", transparent=False, dpi=300)
        plt.close(fig)

    def save_spy_grid(self, path):
        self.save_grid(path, self.spy_grid)

    def save_players_grid(self, path):
        self.save_grid(path, self.played_squares)

    def loc_on_grid(self, word):
        i, j = np.where(utils.format_str(word) == self.formatted_words)
        if i.size == 0 or j.size == 0:
            return None
        return (int(i), int(j))

    def reveal(self, row, column):
        if (
            np.clip(row, 0, self.n_side - 1) != row
            or np.clip(column, 0, self.n_side - 1) != column
        ):
            raise ValueError("({}, {}) is not a valid index".format(row, column))
        # already played square
        if self.played_squares[row, column] != -1:
            new_square = False
            id_color = None
            word = None
        else:
            new_square = True
            id_color = self.spy_grid[row, column]
            self.played_squares[row, column] = id_color
            word = self.words[row, column]

        return new_square, id_color, word

    def play(self, client, global_sender, spies_sender):
        # players subscription
        subscription_message = "+1"
        subscription_end = "fin inscription"
        global_sender.send_message(
            "Codenames: inscription\nPour participer, envoyez {}.\n"
            "Pour commencer le jeu, envoyez {}.".format(
                subscription_message, subscription_end
            )
        )
        players = client.selfSubscription(subscription_message, subscription_end)
        global_sender.send_message("Codenames: fin des inscriptions.")
        random.shuffle(players)

        # define teams
        team_color = ["bleue", "rouge"]
        teams = [players[: len(players) // 2], players[len(players) // 2 :]]
        teams_str = []
        for team in teams:
            team_str = "".join("{}, ".format(player.name) for player in team)[:-2]
            teams_str.append(team_str)

        # define spies
        spies = [teams[0][0], teams[1][0]]
        for spy in spies:
            spies_sender.add_user_id(spy.uid)

        players_grid_path = "players_grid.png"
        spy_grid_path = "spy_grid.png"

        global_sender.send_message("Codenames: debut de la partie")
        # print teams
        str_teams = ""
        for color, team_str, spy in zip(team_color, teams_str, spies):
            str_teams += "équipe {}: {}\nespion: {} {}\n".format(
                color, team_str, spy.first_name, spy.last_name
            )
        global_sender.send_message(str_teams[:-1])
        # send words grid
        self.save_players_grid(players_grid_path)
        global_sender.send_image(players_grid_path, "Grille de mots")
        # send color grid to spies
        self.save_spy_grid(spy_grid_path)
        spies_sender.send_image(spy_grid_path, "Grille espion")

        global_sender.send_message(
            "équipe {}\n"
            "{} à votre tour".format(
                team_color[self.red_playing], teams_str[self.red_playing]
            )
        )

        def play_turn(message, user):
            red_playing = self.red_playing
            end_game = False
            switch_teams = False
            team_playing = teams[red_playing]
            team_uid = [user.uid for user in team_playing]
            valid_message = message.author in team_uid

            text = message.text
            new_square, id_color, word = False, None, None
            if text is None:
                return False

            if valid_message:
                if utils.format_str(text) == "fin du tour":
                    switch_teams = True
                else:
                    loc = self.loc_on_grid(text)
                    if loc is not None:
                        new_square, id_color, word = self.reveal(*loc)

            if new_square:
                square_type = self.idx_to_type[id_color]
                caption = "{} : case {}".format(word, self.type_en_to_fr[square_type])
                self.save_players_grid(players_grid_path)
                global_sender.send_image(players_grid_path, caption)
                if square_type == "lose":
                    global_sender.send_message(
                        "Equipe {}\n{}, vous etes de niveau 93.".format(
                            team_color[red_playing], teams_str[red_playing]
                        )
                    )
                    global_sender.send_message(
                        "Equipe {}\n{}, vous etes digne des 92.".format(
                            team_color[1 - red_playing], teams_str[1 - red_playing]
                        )
                    )
                    end_game = True
                elif id_color != red_playing:
                    switch_teams = True

            if switch_teams:
                red_playing = 1 - red_playing
                self.red_playing = red_playing

            if not end_game:
                global_sender.send_message(
                    "Equipe {}\n"
                    "{} à votre tour".format(
                        team_color[red_playing], teams_str[red_playing]
                    )
                )

            return end_game

        client.processMessages(play_turn, "fin de la partie")
        global_sender.send_message("Fin de la partie.")
