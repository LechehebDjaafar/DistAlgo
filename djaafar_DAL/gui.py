from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Chat System (ADis) Client")

        g_layout = QVBoxLayout()

        # connections label layout
        msg_label_layout = QHBoxLayout()
        msg_label_layout.setContentsMargins(QMargins())

        self.con_status = QLabel('Status: Connecting...', self)
        self.con_status.setAlignment(Qt.AlignRight)
        self.user_lbl = QLabel(None, self)
        self.user_lbl.setAlignment(Qt.AlignRight)
        boldFont = QFont()
        boldFont.setBold(True)
        self.user_lbl.setFont(boldFont)

        msg_label_layout.addWidget(self.con_status, 1)
        msg_label_layout.addWidget(self.user_lbl)

        msg_label_widget = QWidget(self)
        msg_label_widget.setLayout(msg_label_layout)
        g_layout.addWidget(msg_label_widget)
        # end: connections label layout

        # message layout
        msg_input_layout = QHBoxLayout()
        msg_input_layout.setContentsMargins(QMargins())

        self.msg_input = QLineEdit(self)
        self.msg_input.setMinimumSize(200, 22)
        self.msg_input.setDisabled(True)
        self.msg_input.setPlaceholderText('write a message...')
        self.msg_duration = QLineEdit('10', self)
        # self.msg_duration.setMinimumHeight(22)
        self.msg_duration.setValidator(QIntValidator())
        self.msg_duration.setAlignment(Qt.AlignRight)
        self.msg_duration.setMaximumWidth(30)
        self.clients_cb = QComboBox(self)
        self.clients_cb.setMinimumWidth(75)
        self.clients_cb.addItem('<none>')
        # self.clients_cb.setMinimumHeight(22)
        self.send_btn = QPushButton('&Send', self)
        self.send_btn.setDisabled(True)
        self.send_btn.setFixedSize(80, 24)

        msg_input_layout.addWidget(self.msg_input)
        msg_input_layout.addWidget(self.msg_duration)
        msg_input_layout.addWidget(self.clients_cb)
        msg_input_layout.addWidget(self.send_btn)

        msg_widget = QWidget(self)
        msg_widget.setLayout(msg_input_layout)
        g_layout.addWidget(msg_widget)
        # end: message layout

        # local event layout
        local_event_layout = QHBoxLayout()
        local_event_layout.setContentsMargins(QMargins())
        local_event_lbl = QLabel("Create a local event:", self)
        self.local_ev_duration = QLineEdit('5', self)
        # self.local_ev_duration.setMinimumHeight(22)
        self.local_ev_duration.setValidator(QIntValidator())
        self.local_ev_duration.setAlignment(Qt.AlignRight)
        self.local_ev_duration.setMaximumWidth(30)
        self.local_event_btn = QPushButton('Create &Event', self)
        self.local_event_btn.setDisabled(True)
        self.local_event_btn.setFixedSize(80, 24)
        self.local_event_btn.setFixedWidth(80)
        self.status_holder = QLabel("", self)
        self.status_holder.setMinimumWidth(160)
        local_event_layout.addWidget(local_event_lbl, 1)
        local_event_layout.addWidget(self.local_ev_duration)
        local_event_layout.addWidget(self.local_event_btn)
        local_event_layout.addWidget(self.status_holder)

        local_event_widget = QWidget(self)
        local_event_widget.setLayout(local_event_layout)
        g_layout.addWidget(local_event_widget)
        # end: local event layout

        # info layout
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(QMargins())

        # ########## log history layout
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(QMargins())

        # #################### log history header layout
        log_header_layout = QHBoxLayout()
        log_header_layout.setContentsMargins(QMargins())
        log_label = QLabel("Log History:", self)
        log_label.setMinimumHeight(24)
        log_header_layout.addWidget(log_label, 1)
        clear_btn = QPushButton('&Clear Log History', self)
        clear_btn.setFixedWidth(120)
        clear_btn.clicked.connect(lambda _: self.log_history.clear())
        log_header_layout.addWidget(clear_btn)
        log_header_widget = QWidget(self)
        log_header_widget.setLayout(log_header_layout)
        log_layout.addWidget(log_header_widget)
        # #################### end: log history header layout

        self.log_history = QPlainTextEdit()
        self.log_history.setReadOnly(True)
        log_layout.addWidget(self.log_history)
        log_widget = QWidget(self)
        log_widget.setLayout(log_layout)
        info_layout.addWidget(log_widget, 1)
        # ########## end: log history layout

        # ########## table layout
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(QMargins())
        table_label = QLabel("Values Vector:", self)
        table_label.setMinimumHeight(24)
        self.values_table = QTableWidget()
        self.values_table.setMaximumWidth(160)
        self.values_table.setColumnCount(2)
        header = self.values_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.values_table.setHorizontalHeaderLabels(
            ['Process n°', 'Num Value']
        )
        self.values_table.resizeRowsToContents()
        self.values_table.verticalHeader().setVisible(False)
        self.values_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        verticalHeader = self.values_table.verticalHeader()
        verticalHeader.setSectionResizeMode(QHeaderView.Fixed)
        verticalHeader.setDefaultSectionSize(24)
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.values_table)
        table_widget = QWidget(self)
        table_widget.setLayout(table_layout)
        info_layout.addWidget(table_widget)
        # ########## end: table layout

        info_widget = QWidget(self)
        info_widget.setLayout(info_layout)
        g_layout.addWidget(info_widget)
        # end: info layout

        g_widget = QWidget(self)
        g_widget.setLayout(g_layout)

        self.setCentralWidget(g_widget)

    def setNoConnection(self):
        self.con_status.setText('Failed! Name Server Not Initialized')

    def setConnected(self, cl_id: str):
        self.con_status.setText('Connected as')
        self.user_lbl.setText('Process {}'.format(str(cl_id)))
        self.msg_input.setDisabled(False)
        self.local_event_btn.setDisabled(False)
        self.send_btn.setDisabled(False)
        self.msg_input.setFocus()


class ControlWindow(QMainWindow):
    def __init__(self, flags):
        super(ControlWindow, self).__init__(flags=flags)

        self.setWindowTitle("Chat System (ADis) Control")

        g_layout = QVBoxLayout()

        # nameserver layout
        nameserver_layout = QHBoxLayout()
        nameserver_layout.setContentsMargins(QMargins())

        nameserver_lbl = QLabel("Start nameserver:", self)
        self.start_nameserver = QPushButton('&Start', self)

        nameserver_layout.addWidget(nameserver_lbl, 1)
        nameserver_layout.addWidget(self.start_nameserver)

        nameserver_widget = QWidget(self)
        nameserver_widget.setLayout(nameserver_layout)
        g_layout.addWidget(nameserver_widget)
        # end: nameserver layout

        # client layout
        client_layout = QHBoxLayout()
        client_layout.setContentsMargins(QMargins())

        client_lbl = QLabel("Create client(s):", self)
        self.clients_count = QLineEdit('1', self)
        self.clients_count.setValidator(QIntValidator())
        self.clients_count.setAlignment(Qt.AlignRight)
        self.clients_count.setMaximumWidth(30)
        self.create_client = QPushButton('&Create', self)
        self.create_client.setDisabled(True)

        client_layout.addWidget(client_lbl, 1)
        client_layout.addWidget(self.clients_count)
        client_layout.addWidget(self.create_client)

        client_widget = QWidget(self)
        client_widget.setLayout(client_layout)
        g_layout.addWidget(client_widget)
        # end: client layout

        g_widget = QWidget(self)
        g_widget.setLayout(g_layout)

        self.setCentralWidget(g_widget)

    def closeEvent(self, event):
        event.accept()
        sys.exit()


def client_gui() -> MainWindow:
    window = MainWindow()
    window.resize(550, 400)
    window.move(80, 100)
    window.show()
    return window


def control_gui() -> ControlWindow:
    window = ControlWindow(Qt.WindowStaysOnTopHint)
    window.setFixedSize(320, 80)
    window.move(80, 100)
    window.show()
    return window
