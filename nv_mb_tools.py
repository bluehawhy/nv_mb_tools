import sys
import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox

from _src._api import logger, logging_message, config, license_key, license_login
from _src import mb_tools, mb_tools_ui

logging= logger.logger

logging_file_name = logger.log_full_name

version = 'MB Tool v0.1'
revision_list=[
    'Revision list',
    'v0.1 (2022-01-24) : proto type release (beta ver.)'
    ]



config_path ='static\config\config.json'
config_data =config.load_config(config_path)
message_path = config_data['message_path']



def function_app():
    logging_message.remove_message(message_path)
    logging_message.input_message(path = message_path,message = version)
    for revision in revision_list:
        logging_message.input_message(path = message_path,message = revision)
    app = QApplication(sys.argv)
    ex = mb_tools_ui.MyMainWindow(version)
    sys.exit(app.exec_())

def login_app():
    app = QApplication(sys.argv)
    form = license_login.MyMainWindow()
    sys.exit(app.exec_())

    
def prod_app():
    license = license_key.check_License()
    lic_validation = license_key.valild_License(license)
    if lic_validation == True:
        logging.info('license is valild - %s' %str(license))
        function_app()
    else:
        logging.info('license is invalild - %s need up to date' %str(license))
        login_app()
            


def debug_app():
    def get_ssh():
        mb_path = 'static\config\mb_command.json'
        mb_data =config.load_config(mb_path)
        ip = mb_data['ip']
        user = mb_data['user']
        ssh = mb_tools.ssh_connect(ip,user)
        return ssh

    path ='D:\LOG\\trace'
    mb_tools.extract_screenshot_from_trigger(path)
    
    return 0

    
    
if __name__ =='__main__':
    prod_app()

