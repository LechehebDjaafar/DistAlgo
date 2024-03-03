from datetime import datetime
from typing import List, Union, Any, Dict
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Pyro4 import Proxy
from gui import MainWindow
from threading import Thread

import Pyro4
import sys


class ChatServer(QObject):
    new_message_sig = pyqtSignal(int, 'QString', 'QString')
    value_add = pyqtSignal(int, int)
    value_add_to_table = pyqtSignal(int, int)
    value_changed = pyqtSignal(int, int)
    local_event = pyqtSignal()

    def __init__(self, window: MainWindow, app: QApplication, cl_id: int):
        super().__init__(parent=app)
        self.window = window
        self.g_ns: Proxy = None
        self.to_send_cid: int = None
        self.client_id = cl_id
        self.clients: Dict[int, Union[Proxy, ChatServer]] = {}

        self.window.clients_cb.setCurrentIndex(0)
        self.window.closeEvent = self.window_close

        self.daemon = Pyro4.Daemon()
        self.uri = self.daemon.register(self)

        self.new_message_sig.connect(
            self.__update_log__
        )
        self.value_add.connect(self.on_value_add)
        self.value_add_to_table.connect(self.add_to_table)
        self.value_changed.connect(self.update_to_table)
        self.local_event.connect(self.on_local_event_finished)
        self.window.local_event_btn.clicked.connect(self.__trigger_local_ev)

    def on_value_add(self, cid: int, value: int):
        self.add_to_table(cid, value)
        self.add_to_clients_cb(cid)

    def add_to_table(self, cid: int, value: int):
        table_size = self.window.values_table.rowCount()
        for i in range(table_size):
            ele = self.window.values_table.item(i, 0)
            if cid == int(ele.text()):
                return

        self.window.values_table.setRowCount(table_size + 1)
        self.window.values_table.setItem(
            table_size, 0, QTableWidgetItem(str(cid))
        )
        self.window.values_table.setItem(
            table_size, 1, QTableWidgetItem(str(value))
        )

    def update_to_table(self, cid: int, value: int):
        table_size = self.window.values_table.rowCount()
        for i in range(table_size):
            ele = self.window.values_table.item(i, 0)
            if cid == int(ele.text()):
                self.window.values_table.item(i, 1).setText(str(value))
                return

    def add_to_clients_cb(self, cid: int):
        registered_count = self.window.clients_cb.count() - 1
        for i in range(1, registered_count):
            if cid == int(self.window.clients_cb.itemText(i)[8:]):
                return
        self.window.clients_cb.addItem('Process {}'.format(str(cid)))

    def window_close(self, event):
        event.accept()

        if (self.g_ns and hasattr(self.g_ns, 'remove')):
            self.g_ns.remove(
                'hahouari.client.' + 'proc{}'.format(str(self.client_id)),
                str(self.uri)
            )
        self.daemon.unregister(self)
        self.daemon.shutdown()

    def clear_status_holder(self):
        sleep(3)
        self.window.status_holder.setText('')

    def __local_event(self, tow: int):
        sleep(tow/2)
        self.local_event.emit()
        self.window.status_holder.setText('finished local event')
        Thread(target=self.clear_status_holder).start()

    def __trigger_local_ev(self):
        self.window.status_holder.setText('executing local event')
        self.window.send_btn.setDisabled(True)
        self.window.local_event_btn.setDisabled(True)
        tow: int  # time to wait inside local event
        try:
            tow = int(self.window.local_ev_duration)
        except Exception as ex:
            print(ex)
            tow = 5
        Thread(target=self.__local_event, args=(tow,)).start()

    def on_local_event_finished(self):
        # TODO: show local
        text = '[a local event]'
        now = datetime.now()
        c_time = f"{now:%H:%M:%S}"

        self.new_message_sig.emit(self.client_id, text, c_time)

        self.window.send_btn.setDisabled(False)
        self.window.local_event_btn.setDisabled(False)

    def msg_event(self, msg_input: QLineEdit, cids: List[int]):
        if (self.g_ns is None or len(msg_input.text()) == 0):
            return

        text = msg_input.text()
        now = datetime.now()

        data = {
            'id': self.client_id,
            'text': text,
            'time': f"{now:%H:%M:%S}"
        }

        self.new_message_sig.emit(data['id'], data['text'], data['time'])
        self.__send_msg(data, cids)
        self.window.clients_cb.setCurrentIndex(0)
        msg_input.clear()

    def __send_msg(self, data: dict, cids: List[int]):
        if (self.g_ns is None):
            return

        if self.to_send_cid in cids:
            try:
                client = self.clients[self.to_send_cid]
                Thread(target=client.send_msg, args=(data,)).start()
            except Exception as ex:
                print(ex)
                if self.to_send_cid in self.clients:
                    self.clients.pop(self.to_send_cid)

    def __update_log__(self, cl_id: int, text: str, time: str):
        label = '[You]' if cl_id == self.client_id else f'Process {cl_id}'
        self.window.log_history.appendHtml(
            '<b>{} -></b> {} - received at {}'.format(
                label,
                text,
                time
            )
        )

    @Pyro4.expose
    def notify_value_changed(self, cid: int, new_val: int):
        self.value_changed.emit(cid, new_val)

    @Pyro4.expose
    def send_msg(self, data: dict):
        cl_id = data['id']
        text = data['text']
        time = data['time']
        self.new_message_sig.emit(cl_id, text, time)

    @Pyro4.expose
    def update_clients_list(self, data: dict) -> bool:
        try:
            client_uri: str = data['uri']
            cid: int = data['cid']
            if cid in self.clients.keys():
                return
            c_value: str = data['c_value']
            self.value_add.emit(cid, c_value)
            self.clients[cid] = Pyro4.Proxy(client_uri)
            return True
        except Exception as ex:
            print(ex)
            return False

    @Pyro4.expose
    def get_cit(self) -> int:
        return self.client_id
