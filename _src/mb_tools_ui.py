#!/usr/bin/python
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import  Qt, pyqtSlot, QTimer, QTime

from PyQt5.QtGui import QTextCursor
from datetime import date


from _src._api import logger, config, logging_message
from _src import mb_tools

logging = logger.logger
logging_file_name = logger.log_full_name

config_path ='static\config\config.json'
config_data =config.load_config(config_path)
message_path = config_data['message_path']
qss_path  = config_data['qss_path']

logging.debug('qss_path is %s' %qss_path)
logging.debug('config_path is %s' %config_path)


mb_path = 'static\config\mb_command.json'
mb_data =config.load_config(mb_path)

ip = mb_data['ip']
user = mb_data['user']
current_project = ['None']
if len(mb_data['project_list']) != 0:
            current_project = mb_data['project_list']


class MyMainWindow(QMainWindow):
    def __init__(self,title):
        super().__init__()
        self.title = title
        self.today = date.today().strftime('%Y%m%d')
        self.setStyleSheet(open(qss_path, "r").read())
        self.initUI()
        self.show()

    def initUI(self):
        self.statusBar().showMessage('')
        self.setWindowTitle(self.title)
        self.setGeometry(200,200,800,600)
        #self.setFixedSize(600, 480)
        self.form_widget = FormWidget(self, self.statusBar())
        self.setCentralWidget(self.form_widget)


class FormWidget(QWidget):
    def __init__(self, parent,statusbar):
        super(FormWidget, self).__init__(parent)
        self.statusbar_status = 'disconnected'
        self.ssh = 0
        self.project = 0
        self.logging_temp = None
        self.statusbar = statusbar
        self.initUI() 
        self.show()
        self.timer_onescond = QTimer(self)
        self.timer_onescond.timeout.connect(self.thread_for_one_sec)
        self.timer_onescond.start(1000)
        self.timer_tenscond = QTimer(self)
        self.timer_tenscond.timeout.connect(self.thread_for_ten_sec)
        self.timer_tenscond.start(10000)
        

    def initUI(self):
        self.setStyleSheet(open(qss_path, "r").read())
        # make layout
        self.layout_main = QHBoxLayout(self)
        self.layout_fun = QVBoxLayout(self)

        #project layout
        self.layout_project = QHBoxLayout(self)    
        logging.info('project list - %s' %str(current_project))
        self.layout_project.addWidget(QLabel('project: '))
        for project in current_project:
            self.radiobutton = QRadioButton(project)
            self.radiobutton.project = project
            self.radiobutton.toggled.connect(self.on_project_clicked)
            self.layout_project.addWidget(self.radiobutton)
        
        #ssh connected layout
        self.layout_ssh_connect = QGridLayout(self)
        self.ip = mb_data['ip']
        self.line_ip = QLineEdit(self.ip)
        self.button_ssh_connect = QPushButton('connect')
        self.layout_ssh_connect.addWidget(QLabel('ip: ') , 1, 0)
        self.layout_ssh_connect.addWidget(self.line_ip, 1, 1)
        self.layout_ssh_connect.addWidget(self.button_ssh_connect , 1, 2)

        self.layout_ver = QVBoxLayout(self)
        self.qtext_ver_browser = QTextBrowser()
        self.qtext_ver_browser.setReadOnly(1)
        self.qtext_ver_browser.setFixedHeight(100)
        self.label_ver = QLabel('version')
        self.label_ver.setFixedHeight(30)
        self.layout_ver.addWidget(self.label_ver)
        self.layout_ver.addWidget(self.qtext_ver_browser)
        
        #function layout
        self.layout_function = QGridLayout(self)
        self.button_function_0 = QPushButton('user trigger')
        self.button_function_1 = QPushButton('get traffic_sdi_dat')
        self.button_function_2 = QPushButton('get user trigger')
        self.button_function_3 = QPushButton('test3')
        self.button_function_4 = QPushButton('test4')
        self.layout_function.addWidget(self.button_function_0, 0, 0)
        self.layout_function.addWidget(self.button_function_1, 1, 0)
        self.layout_function.addWidget(self.button_function_2, 1, 1)
        self.layout_function.addWidget(self.button_function_3, 2, 0)
        self.layout_function.addWidget(self.button_function_4, 2, 1)

        #log layout
        self.layout_log = QGridLayout(self)
        self.qtext_log_browser = QTextBrowser()
        #self.qtext_log_browser.setFixedWidth(600)
        self.qtext_log_browser.setReadOnly(1)
        self.layout_log.addWidget(self.qtext_log_browser, 1, 0)
        
        #main layout
        self.layout_fun.addLayout(self.layout_project)
        self.layout_fun.addLayout(self.layout_ssh_connect)
        self.layout_fun.addLayout(self.layout_ver)
        self.layout_fun.addLayout(self.layout_function)
        self.layout_main.addLayout(self.layout_fun)
        self.layout_main.addLayout(self.layout_log)
        self.setLayout(self.layout_main)

        #set Alignment
        self.layout_ver.setAlignment(Qt.AlignTop)
        self.layout_project.setAlignment(Qt.AlignLeft)
        self.layout_fun.setAlignment(Qt.AlignTop)
        
        #connect event
        self.button_ssh_connect.clicked.connect(self.on_start)
        self.button_function_0.clicked.connect(self.on_trigger)
        self.button_function_1.clicked.connect(self.on_get_traffic_dat)
        self.button_function_2.clicked.connect(self.on_get_user_trigger)
        #self.button_function_3.clicked.connect(self.on_trigger)
        self.button_function_4.clicked.connect(self.test)

    # add event list
    def open_fileName_dialog(self):
        set_dir = config_data['last_file_path']
        logging.info(set_dir)
        if set_dir == '':
            set_dir = os.path.join(os.path.expanduser('~'),'Desktop')
            logging.info('folder path is %s' %set_dir)
        else:
            logging.info('folder path is %s' %set_dir)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', set_dir, '*' ,options=options)
        if self.file_name == '':
            folder_path = set_dir
        else:
            folder_path = os.path.dirname(self.file_name)
        logging.debug('file path is %s' %self.file_name)
        logging.debug('folder path is %s' %folder_path)
        config_data['last_file_path']=folder_path
        logging.debug(config_data)
        config.save_config(config_data,config_path)
        return self.file_name
    
    def open_folder_name_dialog(self):
        set_dir = config_data['last_file_path']
        logging.info(set_dir)
        if set_dir == '':
            set_dir = os.path.join(os.path.expanduser('~'),'Desktop')
        else:
            logging.info('folder path is %s' %set_dir)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.folder_name = QFileDialog.getExistingDirectory(self, "Select Directory",set_dir)
        if self.folder_name == '':
            pass
        else:
            config_data['last_file_path']=self.folder_name
            logging.debug(config_data)
            config.save_config(config_data,config_path)
        return self.folder_name

    #set tread to change status bar and log browser
    def thread_for_one_sec(self):
        def show_time_statusbar():
            self.statusbar_time = QTime.currentTime().toString("hh:mm:ss")
            self.statusbar_message = self.statusbar_time + '\t-\t' + self.statusbar_status  
            self.statusbar.showMessage(str(self.statusbar_message))
            return 0

        def show_logging():
            with open(message_path, 'r') as myfile:
                self.logging = myfile.read()
            if self.logging_temp == self.logging:
                pass
            else:
                self.qtext_log_browser.setText(self.logging)
                self.logging_temp = self.logging
                self.qtext_log_browser.moveCursor(QTextCursor.End)
            return 0
        show_time_statusbar()
        show_logging()
        return 0
    
    def thread_for_ten_sec(self):
        def check_status_ssh():
            self.ssh_status = mb_tools.check_ssh_connection(self.ssh)
            #logging.debug('statusbar %s - ssh status %s' %(str(self.statusbar_status),str(self.ssh_status)))
            if self.statusbar_status == "disconnected":
                pass
            if self.statusbar_status == "connected" and self.ssh_status is False:
                logging.debug('ssh disconnected')
                self.statusbar_status = "disconnected"
                self.line_ip.setReadOnly(False)
                self.button_ssh_connect.setEnabled(True)
                self.button_ssh_connect.setText('connect')
                self.ssh = 0
                logging_message.input_message(path = message_path, message = '%s@%s has been disconnected.' %('root',self.ip))
        check_status_ssh()
        return 0

    
    @pyqtSlot()
    #change project
    def on_project_clicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            logging.debug("project is %s" % (radioButton.project))
            self.project = radioButton.project
            logging_message.input_message(path = message_path, message = '%s is selected' %(self.project))
            mb_data['current_project']=self.project
            #logging.debug(mb_data)
            config.save_config(mb_data,mb_path)
        return 0

    #ssh connection start
    def on_start(self):
        def connect_ssh():
            logging.info('statusbar_status: %s' %self.statusbar_status)
            self.ip = self.line_ip.text()
            logging.info('ip is %s' %self.ip)
            self.ssh = mb_tools.ssh_connect(self.ip,'root')
            if self.ssh != 0:
                config_data['ip'] = self.ip
                config.save_config(config_data,config_path)
                self.statusbar_status = 'connected'
                self.button_ssh_connect.setText('connected')
                self.line_ip.setReadOnly(True)
                self.button_ssh_connect.setEnabled(False)
                temp_version = ''
                hu_ver, sw_ver, map_ver, ui_ver = mb_tools.get_version(self.ssh)
                map_ver= mb_tools.get_map_version()
                temp_version = temp_version + 'HU version: %s' %hu_ver +'\n'
                temp_version = temp_version + 'Navi version: %s' %sw_ver +'\n'
                temp_version = temp_version + 'Map version: %s' %map_ver +'\n'
                temp_version = temp_version + 'UI version: %s' %ui_ver
                self.qtext_ver_browser.setText(temp_version)
                self.radiobutton.setEnabled(False)

                return self.ssh
            else:
                #if ssh connected fail
                return 0
        if self.statusbar_status == 'disconnected':
            self.ssh = connect_ssh()
            return 0
    
    def test(self):
        self.file_path = self.open_folder_name_dialog()
        logging.info(self.file_path)
    
    #==================================================================
    #function start
    def on_trigger(self):
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected":
            lines = mb_tools.make_trigger(self.ssh)
            return 0
    
    def on_get_traffic_dat(self):
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected":
            traffic_sdi_dat = mb_data[current_project]['traffic_sdi_dat']
            mb_tools.download_file(user,ip,traffic_sdi_dat,path='./static/temp/traffic')
            return 0

    def on_get_user_trigger(self):
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected":
            mb_tools.download_trigger(self.ssh)
            return 0

            
    #==================================================================


        
