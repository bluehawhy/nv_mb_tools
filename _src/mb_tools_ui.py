#!/usr/bin/python
import os
import sys
import time
import threading
import traceback
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QGridLayout, QPlainTextEdit, QFileDialog, QMessageBox, QTextBrowser
from PyQt5.QtCore import pyqtSlot, QTimer, QTime

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

class MyMainWindow(QMainWindow):
    def __init__(self,title):
        super().__init__()
        self.title = title
        self.today = date.today().strftime('%Y%m%d')
        self.setStyleSheet(open(qss_path, "r").read())
        self.initUI()
        self.show()

    def initUI(self):
        self.statusBar().showMessage('Ready')
        self.setWindowTitle(self.title)
        self.setGeometry(200,200,1000,1200)
        #self.setFixedSize(600, 480)
        self.form_widget = FormWidget(self, self.statusBar())
        self.setCentralWidget(self.form_widget)


class FormWidget(QWidget):
    def __init__(self, parent,statusbar):
        super(FormWidget, self).__init__(parent)
        self.statusbar_status = 'not logged in'
        self.session_info = None
        self.logging_temp = None
        self.statusbar = statusbar
        self.initUI() 
        self.show()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.thread_ui)
        self.timer.start(1000)

    def initUI(self):
        self.setStyleSheet(open(qss_path, "r").read())
        # make layout
        self.layout_main = QVBoxLayout(self)
        # login page layout
        self.login_layout = QHBoxLayout(self)
        self.login_layout_id_pw = QGridLayout(self)
        #set user data
        self.user = config_data['id']
        self.password = config_data['password']
        self.line_id = QLineEdit(self.user)       
        self.line_password = QLineEdit(self.password)
        self.line_password.setEchoMode(QLineEdit.Password)
        self.login_import_button = QPushButton('Log In')
        self.login_import_button.setFixedHeight(60)
        self.login_layout_id_pw.addWidget(QLabel('ID') , 1, 0)
        self.login_layout_id_pw.addWidget(QLabel('Password') , 2, 0)
        self.login_layout_id_pw.addWidget(self.line_id, 1, 2)
        self.login_layout_id_pw.addWidget(self.line_password, 2, 2)
        self.login_layout.addLayout(self.login_layout_id_pw)
        self.login_layout.addWidget(self.login_import_button)
        self.layout_main.addLayout(self.login_layout)

        # add log layout
        self.qtext_log_browser = QTextBrowser()
        self.qtext_log_browser.setReadOnly(1)
        self.layout_main.addWidget(self.qtext_log_browser)
        self.setLayout(self.layout_main)

        #login / import event
        self.login_import_button.clicked.connect(self.on_start)
        self.line_password.returnPressed.connect(self.on_start)


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
        file_name, _ = QFileDialog.getOpenFileName(self,  "Open Logwork", set_dir, "Excel Files (*.xlsx)",options=options)
        if file_name == '':
            folder_path = set_dir
        else:
            folder_path = os.path.dirname(file_name)
        logging.debug('file path is %s' %file_name)
        logging.debug('folder path is %s' %folder_path)
        config_data['last_file_path']=folder_path
        logging.debug(config_data)
        config.save_config(config_data,config_path)
        return file_name

    #set tread to change status bar and log browser
    def thread_ui(self):
        def show_time_statusbar():
            self.statusbar_time = QTime.currentTime().toString("hh:mm:ss")
            self.statusbar_message = self.statusbar_time + '\t-\t' + self.statusbar_status  
            self.statusbar.showMessage(str(self.statusbar_message))
          
        def show_logging():
            with open(message_path, 'r') as myfile:
                self.logging = myfile.read()
            if self.logging_temp == self.logging:
                pass
            else:
                self.qtext_log_browser.setText(self.logging)
                self.logging_temp = self.logging
                self.qtext_log_browser.moveCursor(QTextCursor.End)
        show_time_statusbar()
        show_logging()
        return 0
      

    @pyqtSlot()
    def on_start(self):
        if self.statusbar_status == 'not logged in':
            logging_message.input_message(path = message_path,message = 'current not login, start login')
            self.user = self.line_id.text()
            self.password = self.line_password.text()
            self.session_list = rest.initsession(self.user, self.password)
            self.session = self.session_list[0]
            self.session_info = self.session_list[1]
            #fail to login
            if self.session_info == None:
                QMessageBox.about(self, "Login Fail", "please check your password or internet connection")
            #if loggin success
            else:
                self.login_import_button.setText('Import\nTest Cycle')
                self.statusbar_status = 'logged in'
                logging_message.input_message(path = message_path,message = 'user (%s) is logged in' %self.user)
                config_data['id'] = self.user
                config_data['password'] = self.password
                config.save_config(config_data,config_path)
                self.line_id.setReadOnly(1)
                self.line_password.setReadOnly(1)
        else:
            logging_message.input_message(path = message_path, message = 'already logged in, start Test Cycle import~!')
            self.statusbar_status = 'Test Cycle importing~'
            self.file_name = self.open_fileName_dialog()
            logging.info(self.file_name)
            def import_test_cycle():
                self.login_import_button.setEnabled(False)
                #make session
                self.rh = rest.Handler_TestCycle(self.session)
                try:
                    if config_data['import_type'] == 'selenium':
                        test_cycle_selenium.update_test_cycle(self.file_name)
                    elif config_data['import_type'] == 'rest':
                        mb_tools.update_test_cycle(self.rh,self.file_name)
                except Exception as inst:
                    logging.debug(type(inst))
                    logging.debug(inst)
                    logging.debug(traceback.format_exc())
                    logging_message.input_message(path = message_path,message = "there is errer at the point - %s" %str(inst))
                finally:
                    self.login_import_button.setEnabled(True)
                    self.statusbar_status = 'Test Cycle importing done.'
                return 0
            thread_import = threading.Thread(target=import_test_cycle)
            thread_import.start()



        
