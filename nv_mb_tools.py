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

version = 'MB Tool v1.2'
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
    '================================================'
    ]

config_path ='static\config\config.json'
config_data =configus.load_config(config_path)
message_path = config_data['message_path']

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
    #os.system('mode con cols=70 lines=5') if license['user'] != 'miskang' else None
    if lic_validation == True:
        function_cmd()
    else:
        logging.info('license is invalild - %s need up to date' %str(license))
        login_app()
    return 0

def debug_app():
    #mb_tools.target_reset(user='root',ip='10.120.1.91')
    mb_tools.change_default_pos(url = '-33.933382610133464, 151.18100410276847')
    #print(True|True)
    
if __name__ =='__main__':
    debug_app()

