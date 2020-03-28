from getpass import getpass

import click

from boardgames import utils
from boardgames.codenames.codenames import Codenames
from boardgames.com.fb_client import FacebookClient
from boardgames.com.fb_sender import FacebookSender


def disclaimer():
    print(
        "Disclaimer: be careful with this code and fbchat lib in general. Facebook may block your account"
        " for spam or suspicious activities if you send too many messages.\n"
        "This is your responsibility, use it with care."
    )


@click.command()
@click.option(
    "-login", "--login", type=str, required=True, help="Facebook email login",
)
@click.option(
    "-thread",
    "--thread",
    type=int,
    required=True,
    help="ID of the thread to play codenames on."
    " Go to messenger full screen, on the thread of interest, the ID is written at the end page's URL.",
)
@click.option(
    "-group",
    "--group/--no-group",
    default=True,
    is_flag=True,
    help="whether or not the thread is a group (> 2 people)",
)
def main(login, thread, group):
    disclaimer()

    client = FacebookClient(thread, group, login, getpass())
    global_sender = FacebookSender(client)
    if group:
        global_sender.add_group_id(thread)
    else:
        global_sender.add_user_id(thread)
    spies_sender = FacebookSender(client)

    game = Codenames()
    game.reset()
    game.play(client, global_sender, spies_sender)


if __name__ == "__main__":
    main()
