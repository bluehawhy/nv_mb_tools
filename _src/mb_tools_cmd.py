import os, sys


#add internal libary
from _src import mb_tools

refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    from _api import configus
if refer_api == "local":
    from _src._api import configus
#=====================================================

config_path = os.path.join('static','config','config.json')
mb_config_path = os.path.join('static','config','mb_command.json')


class cmd_line:
    def __init__(self, version, revision):
        self.version = version
        self.revision = revision
        self.mb_config_data = configus.load_config(mb_config_path)
        self.config_data = configus.load_config(config_path)

    def main(self):
        os.system('color 0A')
        os.system('mode con cols=100 lines=30')
        os.system('cls')
        print('hello %s' %self.version)
        for r in self.revision:
            print(r)
        
        print('================================================')
        
        print('        current project - %s' %self.mb_config_data['current_project'])
        print('        current ip -      %s' %self.mb_config_data['ip'])
        print('        trigger path -    %s' %self.config_data['last_file_path'])
        print('================================================')
        #===== input menu list =======
        print('#===== input menu list =======')
        print('please enter you want')
        print('01. setup project and ip')
        print('02. check version')
        print('03. make trigger')
        print('04. change binary')
        print('05. change defualt position')
        print('06. remove persistancy')
        print('09. extract screenshot from HU')
        print('10. remount rw')
        print('0. exit')
        select_number = input('please enter number:')
        select_number = int(select_number) if select_number.isdigit() else None

        if select_number == 0 :
            self.exit_main()
            return 0
        elif select_number == 1 :
            self.cmd_update_project_ip()
            return 0
        elif select_number == 2 :
            self.cmd_check_version()
            return 0
        elif select_number == 3 :
            self.cmd_create_trigger()
            return 0
        elif select_number == 4 :
            self.cmd_change_binary()
            return 0
        elif select_number == 5 :
            self.cmd_change_defualt()
            return 0
        elif select_number == 6 :
            self.cmd_remove_per()
            return 0
        elif select_number == 9 :
            self.cmd_extract_HU()
            return 0
        elif select_number == 10 :
            self.cmd_remount()
            return 0
        else:
            self.wrong_select(select_number)
            return 0

    def cmd_temp(self):
        os.system('cls')
        print('please input something,')
        os.system('pause')
        return self.main()

    def wrong_select(self, select_number):
        os.system('cls')
        print(f'you wrote wrong number - {select_number}')
        print(f'please enter correct number')
        os.system('pause')
        return self.main()

    def exit_main(self):
        os.system('cls')
        print('the program is terminated.....')
        os.system('pause')
        return 0


    #===============================================================

    def cmd_change_defualt(self):
        google_loca = input('location or url : ')
        value = mb_tools.change_default_pos(google_loca)
        if value == 1:
            print('please check your location')
            os.system('pause')
            return self.main()
        else:
            print('default position has been changed.')
            os.system('pause')
        return self.main() 

    def cmd_remove_per(self):
        mb_tools.reset_persis()
        return self.main()

    def cmd_update_project_ip(self):
        os.system('cls')
        print('====select project====')
        print('0. skip')
        for i in range(len(self.mb_config_data['project_list'])):
            print('%d. %s' %(i+1,self.mb_config_data['project_list'][i]))
        try:
            self.num_project = int(input('please enter project:'))
        except Exception as E:
            print('please select correct number')
            return self.cmd_update_project_ip()
        if self.num_project == 0:
            pass
        elif self.num_project in range(1,len(self.mb_config_data['project_list'])+1):
            self.mb_config_data['current_project'] = self.mb_config_data['project_list'][self.num_project-1]
        else:
            print('please select correct number')
            return self.cmd_update_project_ip()
        os.system('cls')
        ip = input('please enter ip:')
        self.mb_config_data['ip'] = ip
        self.mb_config_data = configus.save_config(self.mb_config_data,mb_config_path)
        print('updated project ip')
        os.system('pause')
        return self.main()

    def cmd_create_trigger(self):
        os.system('cls')
        print('start user trigger')
        mb_tools.make_trigger(user=self.mb_config_data['user'],ip=self.mb_config_data['ip'])
        c_exit = input('please enter 0, if you exit:')
        if c_exit == '0':
            return self.main()
        else:
            return self.cmd_create_trigger()

    def cmd_check_version(self):
        hu_ver, sw_ver, map_ver, ui_ver = mb_tools.get_version(user=self.mb_config_data['user'],ip=self.mb_config_data['ip'])
        os.system('cls')
        print('start check version')
        print('HU version: %s'% hu_ver)
        print('Navi version: %s'% sw_ver)
        print('Map version: %s'% map_ver)
        print('UI version: %s'% ui_ver)
        os.system('pause')
        return self.main()

    def cmd_extract_HU(self):
        os.system('cls')
        print('start extract HU')
        print('use previous folder, you just press enter - %s' %self.config_data['last_file_path'])
        trigger_folder_path = input('please enter path which trigger stored :')
        if os.path.isdir(trigger_folder_path) is False:
            trigger_folder_path = self.config_data['last_file_path']
            print('path is wrong so use the last path %s' %trigger_folder_path)
            os.system('pause')
        mb_tools.extract_screenshot_from_trigger(trigger_folder_path=trigger_folder_path)
        self.config_data['last_file_path'] = trigger_folder_path
        self.config_data = configus.save_config(self.config_data,config_path)
        print('extract HU done!')
        os.system('pause')
        return self.main()


    def cmd_change_binary(self):
        os.system('cls')
        print('start change binary')
        trigger_folder_path = input('please enter path which navigation in :')
        mb_tools.change_binary(user=self.mb_config_data['user'],ip=self.mb_config_data['ip'],path_pc=trigger_folder_path)
        print('change binary Done.')
        os.system('pause')
        return self.main()

    def cmd_remount(self):
        os.system('cls')
        print('star remount rw,')
        cmd = self.mb_config_data[self.mb_config_data['current_project']]['mount_rw']
        mb_tools.send_by_plink(user=self.mb_config_data['user'],ip=self.mb_config_data['ip'],command=cmd)
        print('remount rw, done')
        os.system('pause')
        return self.main()
