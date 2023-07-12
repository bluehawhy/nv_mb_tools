import os
import sys
import traceback
from PyQt5.QtWidgets import QApplication

from _src._api import logger, logging_message, config, license_key, license_login
from _src import mb_tools, mb_tools_ui, mb_tools_cmd



logging= logger.logger
logging_file_name = logger.log_full_name

version = 'MB Tool v0.7'
revision_list=[
    'Revision list',
    'v0.1 (2022-01-24) : proto type release (beta ver.)',
    'v0.2 (2022-01-27) : merge download trigger and extract sreenshot (beta ver.)\ndisable function button when running.',
    'v0.3 (2022-02-14) : add change binary and open firewall, port',
    'v0.4 (2022-02-23) : Change from ssh (built-in) to putty',
    'v0.5 (2022-04-05) : add trace when critical error',
    'v0.6 (2022-06-20) : add function "mount as rw"',
    'v0.7 (2022-07-12) : add cmd funtion',
    '================================================'
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

def function_cmd():
    cmd_line = mb_tools_cmd.cmd_line(version = version,revision=revision_list)
    cmd_line.main()
    return 0

def login_app():
    app = QApplication(sys.argv)
    form = license_login.MyMainWindow()
    sys.exit(app.exec_())

def prod_app():
    license = license_key.check_License()
    lic_validation = license_key.valild_License(license)
    os.system('color 0A') if license['user'] != 'miskang' else None
    #os.system('mode con cols=70 lines=5') if license['user'] != 'miskang' else None
    if lic_validation == True:
        logging.info('license is valild - %s' %str(license))
        print('which one do you need?')
        print('1. ui')
        print('2. console')
        num_run_type = input('please enter number:')
        if num_run_type == '1':
            function_app()
        else:
            function_cmd()
    else:
        logging.info('license is invalild - %s need up to date' %str(license))
        login_app()
    return 0

def debug_app():
    return 0
    
if __name__ =='__main__':
    prod_app()

