import os, sys
from PyQt5.QtWidgets import QApplication

from _src._api import logger, logging_message, config
from _src import mb_tools, mb_tools_ui
logging= logger.logger

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



def start_app():
    logging_message.remove_message(message_path)
    logging_message.input_message(path = message_path,message = version)
    for revision in revision_list:
        logging_message.input_message(path = message_path,message = revision)
    app = QApplication(sys.argv)
    ex = mb_tools_ui.MyMainWindow(version)
    sys.exit(app.exec_())

def debug_app():
    file = r'D:\_source\python\nv_test_cycle\static\test_cycle_template\E042.1_224741_JPN.xlsx'
    mb_tools.debug_test()
    
if __name__ =='__main__':
    start_app()

