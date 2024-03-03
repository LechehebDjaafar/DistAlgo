import os
import Pyro4
import Pyro4.socketutil
import Pyro4.naming
import Pyro4.core
from typing import List
from adis_utils import SCAlgoChoice
from typing import List, Dict
from PyQt5.QtWidgets import *
from gui import ControlWindow
from client import create_client
from multiprocessing import Process
from threading import Thread


def __threaded_create_ns():
    os.system('python -m Pyro4.naming')


def create_ns():
    ns_thread = Thread(target=__threaded_create_ns)
    ns_thread.start()
    ns_thread.join()


class ControlUtils:
    def __init__(self, controlWindow: ControlWindow):
        super().__init__()
        self.ns_proc: Process = None
        self.clients: Dict[int, Process] = {}
        self.counter = 0
        self.controlWindow = controlWindow
        self.controlWindow.start_nameserver.clicked.connect(
            lambda _: self.on_name_server_start()
        )
        self.controlWindow.create_client.clicked.connect(
            lambda _: self.on_client_create()
        )
        self.controlWindow.closeEvent = self.window_close

    def on_client_create(self):
        try:
            count = int(self.controlWindow.clients_count.text()) or 0
            for i in range(count):
                self.counter += 1
                p = Process(
                    target=create_client,
                    kwargs={
                        'proc_id': self.counter,
                        'algorithm': SCAlgoChoice.lamport_bakery
                    }
                )
                self.clients[self.counter] = p
                p.start()
        except Exception:
            pass
        finally:
            self.controlWindow.clients_count.setText('1')

    def on_name_server_start(self):
        if self.ns_proc is not None and self.ns_proc.is_alive:
            self.ns_proc.terminate()
            self.ns_proc.join()
            self.ns_proc = None
            self.controlWindow.create_client.setDisabled(True)
            self.controlWindow.start_nameserver.setText('&Start')
            for client in self.clients.values():
                if client.is_alive:
                    client.terminate()
                    client.join()
            self.counter = 0
        else:
            self.ns_proc = Process(target=create_ns)
            self.ns_proc.start()

            self.controlWindow.start_nameserver.setText('C&lose')
            self.controlWindow.create_client.setDisabled(False)

    def window_close(self, event):
        event.accept()
        if self.ns_proc is not None and self.ns_proc.is_alive:
            self.ns_proc.terminate()
            self.ns_proc.join()
            for client in self.clients.values():
                if client.is_alive:
                    client.terminate()
                    client.join()
