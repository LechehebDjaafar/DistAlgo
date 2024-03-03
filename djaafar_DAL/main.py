from control import create_control
from multiprocessing import freeze_support


if __name__ == '__main__':
    # Pyinstaller fix to be able to create standalone .exe file
    freeze_support()

    create_control()