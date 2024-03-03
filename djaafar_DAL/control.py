#!/bin/python3

from gui import control_gui
from PyQt5.QtWidgets import *
from control_utils import ControlUtils

import sys


def create_control():
    app = QApplication(sys.argv)
    window = control_gui()
    ControlUtils(window)
    app.exec_()


if __name__ == '__main__':
    create_control()
