import os, sys
from PyQt5.QtWidgets import QApplication


#add internal libary
from _src import mb_tools_cmd, mb_tools

refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
    from _api import loggas, configus, licea
if refer_api == "local":
    from _src._api import loggas, configus, licea
#=====================================================

logging= loggas.logger
logging_file_name = loggas.log_full_name

version = 'MB Tool v1.4'
revision_list=[
    'Revision list',
    'v0.1 (2022-01-24) : proto type release (beta ver.)',
    'v0.2 (2022-01-27) : merge download trigger and extract sreenshot (beta ver.)\ndisable function button when running.',
    'v0.3 (2022-02-14) : add change binary and open firewall, port',
    'v0.4 (2022-02-23) : Change from ssh (built-in) to putty',
    'v0.5 (2022-04-05) : add trace when critical error',
    'v0.6 (2022-06-20) : add function "mount as rw"',
    'v0.7 (2023-07-12) : add cmd funtion',
    'v0.8 (2023-07-12) : add function "change default pos"',
    'v1.0 (2023-11-06) : log fiter implemented.',
    'v1.01 (2023-11-07) : bug fix',
    'v1.1 (2024-01-31) : add some function',
    'v1.2 (2024-02-05) : add reset',
    'v1.3 (2024-04-25) : change trigger function',
    'v1.4 (2024-05-21) : remove some funtions not useful, change putty version',
    '================================================'
    ]

config_path ='static\config\config.json'
message_path = configus.load_config(config_path)['message_path']

def function_cmd():
    cmd_line = mb_tools_cmd.cmd_line(version = version,revision=revision_list)
    cmd_line.main()
    return 0

def login_app():
    app = QApplication(sys.argv)
    form = licea.MyMainWindow()
    sys.exit(app.exec_())

def prod_app():
    license = licea.check_License()
    lic_validation = licea.valild_License(license)
    os.system('color 0A') if license['user'] != 'miskang' else None
    
    config_data =configus.load_config(config_path)
    if os.path.isdir(config_data['last_file_path']) is False:
        logging.info('no dir in local')
        config_data['last_file_path'] = os.path.join(os.path.expanduser('~'),'Desktop')
        config_data = configus.save_config(config_data,config_path)
    if lic_validation == True:
        function_cmd()
    else:
        logging.info('license is invalild - %s need up to date' %str(license))
        login_app()
    return 0

def debug_app():
    mb_tools.get_newest_trigger_number(user = 'root',ip='10.120.1.91')
    
if __name__ =='__main__':
    prod_app()

