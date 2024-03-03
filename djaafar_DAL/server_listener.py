from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from chat_server import ChatServer
from threading import Thread
from gui import MainWindow
import Pyro4


class ServerListener(QThread):

    def __init__(self, window: MainWindow, parent: QApplication, chat_server: ChatServer):
        super(ServerListener, self).__init__(parent)
        self.window = window
        self.chat_server = chat_server

    def run(self):
        Thread(
            target=self.__notify_other_clients__,
            args=(self.window,)
        ).start()
        self.chat_server.daemon.requestLoop()

    def __notify_other_clients__(self, window: MainWindow):
        print("Pyro4.locateNS")
        try:
            self.chat_server.g_ns = Pyro4.locateNS()
        except Exception as ex:
            print(ex)
            window.setNoConnection()
            return
        print("g_ns.register")
        self.chat_server.g_ns.register(
            'hahouari.client.proc{}'.format(str(self.chat_server.client_id)),
            str(self.chat_server.uri)
        )
        self.chat_server.value_add_to_table.emit(
            self.chat_server.client_id,
            self.chat_server.get_msg()
        )
        print("g_ns.list")
        for cl_token, client_uri in self.chat_server.g_ns.list(prefix='hahouari.client.').items():
            if cl_token == 'hahouari.client.proc{}'.format(str(self.chat_server.client_id)):
                continue
            try:
                client: ChatServer = Pyro4.Proxy(client_uri)
                client.update_clients_list({
                    'uri': self.chat_server.uri,
                    'cid': self.chat_server.client_id,
                    'c_value': self.chat_server.get_msg()
                })
                cid = client.get_cit()
                if cid not in self.chat_server.clients.keys():
                    c_value = client.get_msg()
                    self.chat_server.value_add.emit(cid, c_value)
                    self.chat_server.clients[cid] = client
            except Exception as ex:
                print(ex)
                pass
        window.setConnected(cl_id=self.chat_server.client_id)
