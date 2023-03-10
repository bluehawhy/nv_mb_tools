from doctest import master
import os
import sys
from PyQt5.QtWidgets import QApplication

from _src._api import logger, logging_message, config, license_key, license_login
from _src import mb_tools, mb_tools_ui



logging= logger.logger
logging_file_name = logger.log_full_name

version = 'MB Tool v0.3'
revision_list=[
    'Revision list',
    'v0.1 (2022-01-24) : proto type release (beta ver.)',
    'v0.2 (2022-01-27) : merge download trigger and extract sreenshot (beta ver.)\ndisable function button when running.',
    'v0.3 (2022-02-14) : add change binary and open firewall, port',
    'v0.4 (2022-02-23) : Change from ssh (built-in) to putty'
    ]

config_path ='static\config\config.json'
config_data =config.load_config(config_path)
message_path = config_data['message_path']

def function_app():
    logging_message.remove_message(message_path)
    logging_message.input_message(path = message_path,message = version, settime=False)
    for revision in revision_list:
        logging_message.input_message(path = message_path,message = revision, settime=False)
    app = QApplication(sys.argv)
    ex = mb_tools_ui.MyMainWindow(version)
    sys.exit(app.exec_())
    return 0

def login_app():
    app = QApplication(sys.argv)
    form = license_login.MyMainWindow()
    sys.exit(app.exec_())
    return 0

def prod_app():
    license = license_key.check_License()
    lic_validation = license_key.valild_License(license)
    os.system('color 0A') if license['user'] != 'miskang' else None
    os.system('mode con cols=70 lines=5') if license['user'] != 'miskang' else None
    if lic_validation == True:
        logging.info('license is valild - %s' %str(license))
        function_app()
    else:
        logging.info('license is invalild - %s need up to date' %str(license))
        login_app()
            


def debug_app():
    user ='root'
    ip = '10.120.1.91'
    path_pc = r'G:\SW\E048.1_230711' 
    a = mb_tools.download_file(user,ip,'/var/system-version.txt')
    return 0
    
if __name__ =='__main__':
    try:
        debug_app()
    except Exception as E:
        logging.info(E)
        logging_message.input_message(path = message_path,message = str(E))

