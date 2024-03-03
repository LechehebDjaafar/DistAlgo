#!/bin/python3

from gui import client_gui
from chat_server import ChatServer
from server_listener import ServerListener
from PyQt5.QtWidgets import *
from random import choices
from string import digits
from adis_utils import LamportBakery

import sys


def create_client(**kwargs: dict):
    app = QApplication(sys.argv)
    window = client_gui()
    proc_id: int = kwargs['proc_id'] if 'proc_id' in kwargs else int(
        ''.join(choices(digits, k=3))
    )
    server = LamportBakery(window, app, proc_id)
    server_listener = ServerListener(window, app, server)
    server_listener.start()
    app.exec_()


if __name__ == '__main__':
    create_client()
