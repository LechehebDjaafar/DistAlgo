from enum import Enum
from chat_server import ChatServer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Pyro4 import Proxy
from gui import MainWindow
from time import sleep
from typing import List
from threading import Thread

import Pyro4
import sys


class SCAlgoChoice(Enum):
    vector_clock = 1
    lamport_bakery = 2


class LamportBakery(ChatServer):
    choix_rel = pyqtSignal()
    sc_rel = pyqtSignal()

    def __init__(self, window: MainWindow, app: QApplication, client_num: int):
        super().__init__(window, app, client_num)
        self.choix: bool = False
        self.num: int = 0
        self.is_in_sc = False
        self.demanded_sc = False
        self.cids: List[int] = []
        self.window.send_btn.clicked.connect(
            lambda _: self.demander_sc()
        )
        self.choix_rel.connect(self.__check_free_choix)
        self.sc_rel.connect(self.__check_free_sc)

    @Pyro4.expose
    def notify_choix_rel(self):
        self.choix_rel.emit()

    @Pyro4.expose
    def notify_sc_rel(self):
        self.sc_rel.emit()

    @Pyro4.expose
    def cl_choix(self) -> bool:
        return self.choix

    @Pyro4.expose
    def get_msg(self) -> int:
        return self.num

    def get_choix(self, i: int) -> bool:
        if i == self.client_id:
            return self.choix
        else:
            try:
                return self.clients[i].cl_choix()
            except Exception as ex:
                print(ex)
                return False

    def get_num(self, i: int, onerror_val: int) -> int:
        if i == self.client_id:
            return self.num
        else:
            try:
                return self.clients[i].get_msg()
            except Exception as ex:
                print(ex)
                if i in self.clients.keys():
                    self.clients.pop(i)
                return onerror_val

    def __exit_sc(self):
        self.is_in_sc = False
        self.demanded_sc = False
        self.num = 0
        self.notify_value_changed(self.client_id, self.num)
        self.window.send_btn.setDisabled(False)
        self.window.local_event_btn.setDisabled(False)
        self.window.status_holder.setText('exited critical section')
        Thread(target=self.clear_status_holder).start()
        for cid in self.cids:
            if cid not in self.clients.keys():
                continue
            self.clients[cid].notify_sc_rel()
            self.clients[cid].notify_value_changed(self.client_id, self.num)
        self.cids = []

    def section_critique(self, tow: int):
        self.is_in_sc = True
        sleep(tow / 2)
        self.msg_event(self.window.msg_input, self.cids)
        self.__exit_sc()

    def get_min_estampille(self):
        if (all(self.get_num(cid, 0) == 0 for cid in self.cids)):
            return self.client_id

        min_cid = self.client_id
        min_num = self.num

        for cid in self.cids:
            c_num = self.get_num(cid, sys.maxsize)
            print(f'proc[{cid}]: num =[{c_num}]')
            if c_num == 0:
                # does not want section critique
                continue
            if (c_num > min_num):
                # [cid] want sc but [min_cid] have priority
                continue
            elif (c_num == min_num and cid > min_cid):
                # [cid] want sc but [min_cid] have priority
                continue
            else:
                # [cid] has priority and not [client_id]
                min_cid = cid
                min_num = c_num
        return min_cid

    def __check_free_sc(self):
        print('check_free_sc')
        if (not self.demanded_sc):
            return
        print('demanded_sc')
        min_cid = self.get_min_estampille()
        if min_cid != self.client_id:
            self.window.status_holder.setText(
                f'waiting process {min_cid} to free'
            )
            print(f'[{min_cid}] is before me [{self.client_id}]')
            return
        self.window.status_holder.setText('holding critical section')
        print(f'I have right to enter [{self.client_id}]')

        tow: int  # time to wait inside section critique
        try:
            tow = int(self.window.msg_duration.text())
        except Exception as ex:
            print(ex)
            tow = 10

        Thread(
            target=self.section_critique,
            args=(tow,)
        ).start()

    def __check_free_choix(self):
        print('check_free_choix')
        if (not self.demanded_sc):
            return
        if (any(self.get_choix(cid) for cid in self.cids)):
            return
        self.window.status_holder.setText('waiting critical section to free')
        self.__check_free_sc()

    def demander_sc(self):
        if len(self.window.msg_input.text()) == 0:
            return
        if self.demanded_sc:
            return
        print('demanded_sc')
        if self.window.clients_cb.currentText() == '<none>':
            return
        print('to_send process is setteled')

        self.window.send_btn.setDisabled(True)
        self.window.local_event_btn.setDisabled(True)
        self.demanded_sc = True
        self.cids = list(self.clients.keys())
        self.to_send_cid = int(self.window.clients_cb.currentText()[8:])
        self.choix = True
        clients_max_num = 0
        if (len(self.cids) > 0):
            clients_max_num = max(self.get_num(cid, 0) for cid in self.cids)
        self.num = 1 + max(clients_max_num, self.num)
        self.value_changed.emit(self.client_id, self.num)
        self.choix = False
        for cid in self.cids:
            try:
                self.clients[cid].notify_choix_rel()
                self.clients[cid].notify_value_changed(
                    self.client_id, self.num
                )
            except Exception as ex:
                print(ex)
                if cid in self.clients.keys():
                    self.clients.pop(cid)
        self.window.status_holder.setText('waiting choix[j] to be set False')
        self.__check_free_choix()
