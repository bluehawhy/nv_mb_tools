#!/usr/bin/python
import os, sys
import threading
import time
import traceback
from datetime import date

from PyQt5.QtWidgets import *
from PyQt5.QtCore import  Qt, pyqtSlot, QTimer, QTime
from PyQt5.QtGui import QTextCursor



#add internal libary
from _src import mb_tools

refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    from _api import loggas, configus
if refer_api == "local":
    from _src._api import loggas, configus
#=====================================================

config_path = os.path.join('static','config','config.json')
mb_config_path = os.path.join('static','config','mb_command.json')

logging = loggas.logger
logging_file_name = loggas.log_full_name

config_path ='static\config\config.json'
mb_path = 'static\config\mb_command.json'

class MyMainWindow(QMainWindow):
    def __init__(self,title):
        super().__init__()
        self.title = title
        self.today = date.today().strftime('%Y%m%d')
        self.config_data =configus.load_config(config_path)
        self.message_path = self.config_data['message_path']
        self.qss_path  = self.config_data['qss_path']
        self.setStyleSheet(open(self.qss_path, "r").read())
        self.initUI()
        self.show()

    def initUI(self):
        self.statusBar().showMessage('00:00:00 - disconnected')
        self.setWindowTitle(self.title)
        self.setGeometry(200,200,800,600)
        #self.setFixedSize(800,600)
        self.form_widget = FormWidget(self, self.statusBar())
        self.setCentralWidget(self.form_widget)


class FormWidget(QWidget):
    def __init__(self, parent,statusbar):
        super(FormWidget, self).__init__(parent)
        self.statusbar_status = 'disconnected'
        self.ssh = 0
        self.config_data =configus.load_config(config_path)
        self.message_path = self.config_data['message_path']
        self.qss_path  = self.config_data['qss_path']
        self.mb_data =configus.load_config(mb_path)
        self.ip = self.mb_data['ip']
        self.user = self.mb_data['user']
        self.project_list = ['None']
        if len(self.mb_data['project_list']) != 0:
            self.project_list = self.mb_data['project_list']
        self.current_project = self.mb_data['current_project']
        self.logging_temp = None
        
        self.set_dir = self.config_data['last_file_path']
        
        self.statusbar = statusbar
        self.version_txt = ''
        self.new_version_txt = ''
        self.logging = ''
        self.radio_button_group= []
        self.function_button_group= []
        self.function_group= []
        self.initUI() 
        self.show()
        self.timer_onescond = QTimer(self)
        self.timer_onescond.timeout.connect(self.thread_for_one_sec)
        self.timer_onescond.start(1000)
        self.timer_tenscond = QTimer(self)
        self.timer_tenscond.timeout.connect(self.thread_for_ten_sec)
        self.timer_tenscond.start(10000)
        self.timer_hunscond = QTimer(self)
        self.timer_hunscond.timeout.connect(self.thread_for_hun_sec)
        self.timer_hunscond.start(100000)
        

    def initUI(self):
        self.setStyleSheet(open(self.qss_path, "r").read())
        # make layout
        self.layout_main = QHBoxLayout(self)
        self.layout_fun = QVBoxLayout(self)

        #project layout
        self.layout_project = QHBoxLayout(self)    
        logging.info('project list - %s' %str(self.project_list))
        self.layout_project.addWidget(QLabel('project: '))
        
        for self.project in self.project_list:
            self.radiobutton = QRadioButton(self.project)
            self.radio_button_group.append(self.radiobutton)
            self.radiobutton.project = self.project
            if self.project == self.current_project:
                self.radiobutton.setChecked(True)
            self.radiobutton.toggled.connect(self.on_project_clicked)
            self.layout_project.addWidget(self.radiobutton)
        
        #ssh connected layout
        self.layout_ssh_connect = QGridLayout(self)
        self.ip = self.mb_data['ip']
        self.line_ip = QLineEdit(self.ip)
        self.button_ssh_connect = QPushButton('connect')
        self.layout_ssh_connect.addWidget(QLabel('ip: ') , 1, 0)
        self.layout_ssh_connect.addWidget(self.line_ip, 1, 1)
        self.layout_ssh_connect.addWidget(self.button_ssh_connect , 1, 2)

        #add version field.
        self.layout_ver = QVBoxLayout(self)
        self.qtext_ver_browser = QTextBrowser()
        self.qtext_ver_browser.setReadOnly(1)
        self.qtext_ver_browser.setFixedHeight(100)
        self.label_ver = QLabel('version')
        self.label_ver.setFixedHeight(30)
        self.layout_ver.addWidget(self.label_ver)
        self.layout_ver.addWidget(self.qtext_ver_browser)
        
        #add path field.
        self.layout_path = QVBoxLayout(self)
        self.layout_path_1 = QHBoxLayout(self)
        self.qline_path = QLineEdit(self.set_dir)
        self.label_path = QLabel('current path')
        self.button_open_folder = QPushButton('open folder')
        self.function_group.append(self.qline_path)
        self.qline_path.setFixedHeight(30)
        self.label_path.setFixedHeight(30)
        self.button_open_folder.setFixedSize(100,30)
        self.layout_path_1.addWidget(self.qline_path)
        self.layout_path_1.addWidget(self.button_open_folder)
        self.layout_path.addWidget(self.label_path)
        self.layout_path.addLayout(self.layout_path_1)
        

        #function layout
        self.layout_function = QVBoxLayout(self)
        
        #function layout for number
        self.layout_function_line = QHBoxLayout(self)
        self.label_function = QLabel('select number and enter (1~8):')
        self.qline_function = QLineEdit('')
        self.layout_function_line.addWidget(self.label_function)
        self.layout_function_line.addWidget(self.qline_function)
        
        

        self.layout_function_button = QGridLayout(self)
        self.button_user_trigger = QPushButton('user trigger')
        self.button_get_traffic_sdi = QPushButton('get traffic_sdi_dat')
        
        self.button_extract_screenshot_from_HU = QPushButton('extract screenshot')
        self.button_test2 = QPushButton('test 2')
        self.button_change_default_pos = QPushButton('change default pos')
        self.button_mount_rw = QPushButton('mount as rw')
        self.button_open_port = QPushButton('open port\n disable firewall')
        self.button_change_binary = QPushButton('change binary')
        self.layout_function_button.addWidget(self.button_user_trigger, 0, 0)
        self.layout_function_button.addWidget(self.button_mount_rw, 3, 1)
        self.layout_function_button.addWidget(self.button_get_traffic_sdi, 2, 0)
        self.layout_function_button.addWidget(self.button_extract_screenshot_from_HU, 3, 0)
        self.layout_function_button.addWidget(self.button_test2, 0, 1)
        self.layout_function_button.addWidget(self.button_change_default_pos, 1, 1)
        self.layout_function_button.addWidget(self.button_open_port, 2, 1)
        self.layout_function_button.addWidget(self.button_change_binary, 1, 0)
        self.layout_function.addLayout(self.layout_function_line)
        self.layout_function.addLayout(self.layout_function_button)

        
        #set functional group
        self.function_group.append(self.button_user_trigger)
        self.function_group.append(self.button_get_traffic_sdi)
        self.function_group.append(self.button_mount_rw)
        self.function_group.append(self.button_extract_screenshot_from_HU)
        self.function_group.append(self.button_test2)
        self.function_group.append(self.button_change_default_pos)
        self.function_group.append(self.button_open_port)
        self.function_group.append(self.button_change_binary)
        self.function_group.append(self.qline_function)

        for self.button_function in self.function_group:
            self.button_function.setEnabled(False)
        self.button_extract_screenshot_from_HU.setEnabled(True)

        #log layout
        self.layout_log = QGridLayout(self)
        self.qtext_log_browser = QTextBrowser()
        #self.qtext_log_browser.setFixedWidth(400)
        self.qtext_log_browser.setReadOnly(1)
        self.qtext_log_browser.setFontPointSize(8)
        self.layout_log.addWidget(self.qtext_log_browser, 1, 0)
        
        #main layout
        self.layout_fun.addLayout(self.layout_project)
        self.layout_fun.addLayout(self.layout_ssh_connect)
        self.layout_fun.addLayout(self.layout_ver)
        self.layout_fun.addLayout(self.layout_path)
        self.layout_fun.addLayout(self.layout_function)
        self.layout_main.addLayout(self.layout_fun)
        self.layout_main.addLayout(self.layout_log)
        self.setLayout(self.layout_main)

        #set Alignment
        self.layout_ver.setAlignment(Qt.AlignTop)
        self.layout_project.setAlignment(Qt.AlignLeft)
        self.layout_fun.setAlignment(Qt.AlignTop)
        
        #connect event
        self.qline_function.returnPressed.connect(self.on_start_function_number)
        self.button_ssh_connect.clicked.connect(self.on_start_connect_ssh)
        self.line_ip.returnPressed.connect(self.on_start_connect_ssh)
        self.qline_path.returnPressed.connect(self.on_change_path)
        self.button_user_trigger.clicked.connect(self.on_trigger)
        self.button_get_traffic_sdi.clicked.connect(self.on_get_traffic_dat)
        self.button_extract_screenshot_from_HU.clicked.connect(self.on_extract_screenshot_from_HU)
        self.button_open_port.clicked.connect(self.on_open_port)
        self.button_test2.clicked.connect(self.on_test)
        self.button_change_default_pos.clicked.connect(self.on_change_default_pos)
        self.button_mount_rw.clicked.connect(self.on_mount_rw)
        self.button_open_folder.clicked.connect(self.on_open_folder)
        self.button_change_binary.clicked.connect(self.on_change_binary)

    # add event list
    def open_fileName_dialog(self):
        self.set_dir = self.config_data['last_file_path']
        logging.info(self.set_dir)
        if self.set_dir == '':
            self.set_dir = os.path.join(os.path.expanduser('~'),'Desktop')
            logging.info('folder path is %s' %self.set_dir)
        else:
            logging.info('folder path is %s' %self.set_dir)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', self.set_dir, '*' ,options=options)
        if file_name == '':
            pass
        else:
            folder_path = os.path.dirname(file_name)
            self.config_data['last_file_path']=folder_path
            self.config_data = configus.save_config(self.config_data,config_path)
        return file_name
    
    def open_folder_name_dialog(self):
        self.set_dir = self.config_data['last_file_path']
        if self.set_dir == '':
            temp_folder = os.path.join(os.path.expanduser('~'),'Desktop')
        else:
            logging.info('folder path is %s' %self.set_dir)
            temp_folder = self.set_dir
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        temp_folder = QFileDialog.getExistingDirectory(self, "Select Directory",temp_folder)
        if temp_folder == '':
            pass
        else:
            self.config_data['last_file_path']=temp_folder
            self.config_data = configus.save_config(self.config_data,config_path)
        return temp_folder

    def open_folder_name_dialog_no_save(self):
        temp_folder = os.path.join(os.path.expanduser('~'),'Desktop')
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        temp_folder = QFileDialog.getExistingDirectory(self, "Select Directory",temp_folder)
        return temp_folder


    def set_function_button(self,value=True):
        for self.button_function in self.function_group:
            self.button_function.setEnabled(value)
        return 0
    
    def set_function_button_disconnected(self,value=True):
        self.button_extract_screenshot_from_HU.setEnabled(value)
        self.button_ssh_connect.setEnabled(value)
        return 0


    #set tread to change status bar and log browser
    #============== thread function list ===========================
    def show_time_statusbar(self):
            self.statusbar_time = QTime.currentTime().toString("hh:mm:ss")
            self.statusbar_message = self.statusbar_time + '\t-\t' + self.statusbar_status  
            self.statusbar.showMessage(str(self.statusbar_message))
            return 0
    
    def show_logging(self):
            with open(self.message_path, 'r') as myfile:
                self.logging = myfile.read()
            if self.logging_temp == self.logging:
                pass
            else:
                self.qtext_log_browser.setText(self.logging)
                self.logging_temp = self.logging
                self.qtext_log_browser.moveCursor(QTextCursor.End)
            return 0
    def show_current_verssion(self):
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected":
            if self.new_version_txt == self.version_txt: #pass if new and current are same else update
                #logging.info('pass due to same version')
                pass
            else:
                logging.info('show_current_verssion() - new version detected so update version box')
                self.version_txt = self.new_version_txt #sync version and new one
                self.qtext_ver_browser.setText(self.version_txt)
        return 0

    def check_status_ssh(self):
        self.ssh_status = mb_tools.check_ssh_connection(self.ssh)
        #logging.info(self.ssh_status)
        logging.debug('statusbar %s - ssh status %s' %(str(self.statusbar_status),str(self.ssh_status)))
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected" and self.ssh_status is False:
            logging.debug('ssh disconnected')
            self.statusbar_status = "disconnected"
            self.line_ip.setReadOnly(False)
            self.button_ssh_connect.setEnabled(True)
            self.button_ssh_connect.setText('connect')
            self.ssh = 0
            self.set_function_button(False)
            loggas.input_message(path = self.message_path, message = '%s@%s has been disconnected.' %('root',self.ip))
        return 0
    
    def check_current_path(self):
        self.set_dir = self.config_data['last_file_path']
        self.qline_path.setText(self.set_dir)
        return 0

    def get_current_version(self):
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected":
            self.new_version_txt = self.call_version_into_textbox()
        return 0


    #============== call function by time thread ===========================
    def thread_for_one_sec(self):
        self.show_time_statusbar()
        self.show_logging()
        return 0
    
    def thread_for_ten_sec(self):
        self.check_status_ssh()
        self.show_current_verssion()
        return 0


    def thread_for_hun_sec(self):
        self.get_current_version()
        return 0
    
    @pyqtSlot()    
    #change project
    def on_project_clicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            logging.debug("project is %s" % (radioButton.project))
            self.current_project = radioButton.project
            loggas.input_message(path = self.message_path, message = '%s is selected' %(self.current_project))
            self.mb_data['current_project']=self.current_project
            #logging.debug(mb_data)
            self.mb_data = configus.save_config(self.mb_data,mb_path)
            
        return 0

    #ssh connection start
    def on_start_connect_ssh(self):
        def connect_ssh():
            self.button_ssh_connect.setEnabled(False)
            logging.info('statusbar_status: %s' %self.statusbar_status)
            self.ip = self.line_ip.text()
            logging.info('ip is %s' %self.ip)
            self.ssh = mb_tools.ssh_connect(self.user,self.ip)
            if self.ssh != 0:
                self.mb_data['ip'] = self.ip
                self.mb_data = configus.save_config(self.mb_data,mb_path)
                self.line_ip.setReadOnly(True)
                self.button_ssh_connect.setEnabled(False)
                for self.radiobutton in self.radio_button_group:
                    self.radiobutton.setEnabled(False)
                self.set_function_button(True)
                self.statusbar_status = 'connected'
                self.button_ssh_connect.setText('connected')
                self.new_version_txt = self.call_version_into_textbox()
                return self.ssh
            else:
                #if ssh connected fail
                self.button_ssh_connect.setEnabled(True)
                return 0

        if self.statusbar_status == 'disconnected':
            thread_import = threading.Thread(target=connect_ssh)
            thread_import.start()
            return 0
    
    #==================================================================
    #function start
    def call_version_into_textbox(self):
        try:
            hu_ver, sw_ver, map_ver, ui_ver = mb_tools.get_version(self.user,self.ip)
        except Exception as E:
            logging.critical(traceback.format_exc())
            loggas.input_message(path = self.message_path, message = f'there is error on_change_binary')
            loggas.input_message(path = self.message_path, message = f'contact the admin for more information')
            hu_ver, sw_ver, map_ver, ui_ver = None     
        temp_version = ''
        temp_version = temp_version + 'HU version: %s' %hu_ver +'\n'
        temp_version = temp_version + 'Navi version: %s' %sw_ver +'\n'
        temp_version = temp_version + 'Map version: %s' %map_ver +'\n'
        temp_version = temp_version + 'UI version: %s' %ui_ver
        return temp_version

    def on_start_function_number(self):
        self.function_number = self.qline_function.text()
        loggas.input_message(path = self.message_path, message = f'you entered {self.function_number}')
        if self.statusbar_status == "disconnected":
             self.qline_function.setText('')
             return 0
        if not self.function_number.isdigit():
            loggas.input_message(path = self.message_path, message = f'please enter number.')
            self.qline_function.setText('')
            return 0
        self.function_number = int(self.qline_function.text())
        if self.function_number == 99:
            loggas.input_message(path = self.message_path, message = f'hidden one. get HU trigger from HU')
            self.on_get_user_trigger()
            self.qline_function.setText('')
            return 0
        if self.function_number > 8:
            loggas.input_message(path = self.message_path, message = f'please enter number under 8.')
            self.qline_function.setText('')
            return 0
        else:
            self.on_trigger() if self.function_number == 1 else None
            None if self.function_number == 2 else None
            self.on_change_binary() if self.function_number == 3 else None
            None if self.function_number == 4 else None
            None if self.function_number == 5 else None
            self.on_open_port() if self.function_number == 6 else None
            self.on_extract_screenshot_from_HU() if self.function_number == 7 else None
            None if self.function_number == 8 else None
            self.qline_function.setText('')
        return 0
    
    def on_open_folder(self):
        #check self.set_dir
        if os.path.isdir(self.set_dir) is True:
            loggas.input_message(path = self.message_path, message = f'open folder - {self.set_dir}')
            os.startfile(self.set_dir)
        else:
            loggas.input_message(path = self.message_path, message = f'there is no folder - {self.set_dir}')
            self.set_dir = os.path.join(os.path.expanduser('~'),'Desktop')
            self.config_data['last_file_path']=self.set_dir
            self.config_data = configus.save_config(self.config_data,config_path)
            self.set_dir = self.config_data['last_file_path']
            self.qline_path.setText(self.set_dir)
            os.startfile(self.set_dir)
        return 0
    
    def on_change_binary(self):
        self.binary_folder_name = self.open_folder_name_dialog_no_save()
        loggas.input_message(path = self.message_path, message = f'folder path - {self.binary_folder_name}')
        def start():
            if self.binary_folder_name != '':
                self.set_function_button(False)
                try:
                    mb_tools.change_binary(self.user,self.ip,self.binary_folder_name)
                except Exception as E:
                    logging.critical(traceback.format_exc())
                    loggas.input_message(path = self.message_path, message = f'there is error on_change_binary')
                    loggas.input_message(path = self.message_path, message = f'contact the admin for more information')
                self.set_function_button(True)
                self.new_version_txt = self.call_version_into_textbox()
                return 0
            else:
                return 0
        thread_import = threading.Thread(target=start)
        thread_import.start()
        return 0
        
    def on_change_path(self):
        self.check_folder_name = self.qline_path.text()
        #logging.info(self.check_folder_name)
        #logging.info(os.path.isdir(self.check_folder_name))
        if os.path.isdir(self.check_folder_name) == True:
            self.config_data['last_file_path']=self.check_folder_name
            self.config_data = configus.save_config(self.config_data,config_path)
            self.set_dir = self.config_data['last_file_path']
            loggas.input_message(path = self.message_path, message = f'change path - {self.check_folder_name}')
        else:
            self.qline_path.setText(self.set_dir)
            loggas.input_message(path = self.message_path, message = f'path is not exist - {self.check_folder_name}')
        return 0

    def on_mount_rw(self):
        logging.info('start mount as rw')
        loggas.input_message(path = self.message_path, message = f'start mount as rw')
        cmd = self.mb_data[self.current_project]['mount_rw']
        mb_tools.send_by_plink(self.user,self.ip,cmd)
        return 0

    def on_open_port(self):
        logging.info('start open port or firewall disable')
        loggas.input_message(path = self.message_path, message = f'start open port or firewall disable')
        cmd = self.mb_data[self.current_project]['open_port']
        #logging.info(cmd)
        try:
            mb_tools.send_by_plink(self.user,self.ip,cmd)
        except Exception as E:
            logging.critical(traceback.format_exc())
            loggas.input_message(path = self.message_path, message = f'there is error on_open_port')
            loggas.input_message(path = self.message_path, message = f'contact the admin for more information')
        return 0
 
    def on_trigger(self):
        loggas.input_message(path = self.message_path, message = f'start make trigger.')
        def start():
            if self.statusbar_status == "disconnected":
                pass
            if self.statusbar_status == "connected":
                try:
                    now, lines = mb_tools.make_trigger(user=self.user,ip=self.ip)
                    time.sleep(20)
                    mb_tools.get_tmp_screenshot(user = 'root', ip=self.ip,path=self.set_dir,trigger_time=now)
                except Exception as E:
                    logging.critical(traceback.format_exc())
                    loggas.input_message(path = self.message_path, message = f'there is error on_trigger')
                    loggas.input_message(path = self.message_path, message = f'contact the admin for more information')
                return 0
        thread_import = threading.Thread(target=start)
        thread_import.start()
        return 0

    def on_get_traffic_dat(self):
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected":
            self.folder_path = self.open_folder_name_dialog()
            def start():
                if self.folder_path =='':
                    pass
                else:
                    try:
                        mb_tools.get_traffic_sdi_dat(self.ssh,self.user,self.ip,path=self.folder_path)
                    except Exception as E:
                        logging.critical(traceback.format_exc())
                        loggas.input_message(path = self.message_path, message = f'there is error on_trigger')
                        loggas.input_message(path = self.message_path, message = f'contact the admin for more information')       
                return 0
            thread_import = threading.Thread(target=start)
            thread_import.start()
        return 0

    def on_get_user_trigger(self):
        if self.statusbar_status == "disconnected":
            pass
        if self.statusbar_status == "connected":
            self.folder_path = self.open_folder_name_dialog()
            def start():
                self.set_function_button(False)
                if self.folder_path =='':
                    pass
                else:
                    E = mb_tools.get_trigger_screenshot(self.folder_path)
                self.set_function_button(True)
                return 0
            thread_import = threading.Thread(target=start)
            thread_import.start()
        return 0
    
    def on_change_default_pos(self):
        loggas.input_message(path = self.message_path, message = f'change default position')
        google_loca, ok = QInputDialog.getText(self, 'url', 'Enter url:')
        logging.info(f'this is url - {google_loca}, input status - {ok}')
        loggas.input_message(path = self.message_path, message = f'this is url - {google_loca}')
        mb_tools.change_default_pos(google_loca)
        return 0

    def on_test(self):
        loggas.input_message(path = self.message_path, message = f'test button')
        return 0

    def on_extract_screenshot_from_HU(self):
        self.folder_path = self.open_folder_name_dialog()
        def start():
            if self.folder_path =='':
                pass
            else:
                self.set_function_button(False)
                mb_tools.extract_screenshot_from_trigger(self.folder_path)
                if self.statusbar_status == "disconnected":
                    self.set_function_button_disconnected()
                if self.statusbar_status == "connected":
                    self.set_function_button(True)
            return 0
        thread_import = threading.Thread(target=start)
        thread_import.start()
        return 0
    #==================================================================


        
