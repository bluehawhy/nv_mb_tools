# -*- coding: utf-8 -*-
#!/usr/bin/python
import sqlite3
import paramiko
import os, sys
import datetime
import shutil
import re
import traceback



#add internal libary

refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    from _api import loggas, configus, xmlas
if refer_api == "local":
    from _src._api import loggas, configus, xmlas
#=====================================================
#make logpath
logging= loggas.logger

#loading config data
config_path = 'static\config\config.json'
config_data =configus.load_config(config_path)
qss_path = config_data['qss_path']
message_path = config_data['message_path']
test_cycle_url = config_data['test_cycle_url']

mb_path = 'static\config\mb_command.json'


## ============================================================
## thosre are basic functions - refer to other functions
def add_known_hosts(user,ip): #return type : 0
    os.system('del %s' %os.path.join(os.path.expanduser('~'),'.ssh','known_hosts'))
    command = 'ssh -o StrictHostKeyChecking=no %s@%s echo -n' %(user,ip)
    os.system(command)
    return 0
    
def autostoring_cache_plink(user,ip): #return type : 0
    command = f'echo y | static\\tool\putty\plink.exe {user}@{ip} "exit"'
    os.system(command)
    return 0
    
def send_by_ssh(ssh,command): #return type : str
    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    temp_line =''
    for line in lines:
        #logging.debug(line)
        temp_line = temp_line + line
    return temp_line 

def send_by_plink(user,ip,command): #return type : str
    command = f'static\\tool\putty\plink.exe -no-antispoof {user}@{ip} "{command}" > static\\temp\plink.txt'
    os.system(command)
    f = open("static\\temp\plink.txt", "r")
    lines =f.read()
    return lines

def file_check_in_target(user,ip,file = None): #return type : bool
    check_value = False
    command = f'ls {file}'
    line = send_by_plink(user,ip,command)
    if file in line:
        check_value = True
    return check_value

def file_check_in_pc(file = None,path='./static/temp'): #return type : bool
    check_value = False
    loca_file_path = os.path.join(path,os.path.basename(file))
    if os.path.exists(loca_file_path) is True:
        check_value =  True
        #logging.info(f'file already exist - {loca_file_path}')
    return check_value

def download_file(user,ip,file,path='./static/temp'): #return type : bool, str
    file_in_pc = file_check_in_pc(file,path)
    file_in_target = file_check_in_target(user,ip,file)
    download_path = ''
    download_result = False
    if file_in_pc is True or file_in_target is False:
        logging.info(f'file_in_pc: {file_in_pc}') if file_in_pc == True else None
        logging.info(f'file_in_target: {file_in_target} - {file}') if file_in_target == False else None
        return download_result , download_path
    else:
        command = f'static\\tool\putty\pscp.exe "{user}@{ip}:{file}" "{path}"' 
        os.system(command)
        download_path = os.path.join(path,os.path.basename(file))
        download_result = True
        return download_result, download_path

def uploadfile(user,ip,file_in_pc,path_target): #return type : 0
    file_in_target = file_check_in_target(user,ip,f'{path_target}/{os.path.basename(file_in_pc)}')
    if file_in_target is True:
        logging.info(f'file_in_target: {file_in_target}')
    else:
        command = f'static\\tool\putty\pscp.exe "{file_in_pc}" "{user}@{ip}:{path_target}"'
        #logging.info(command)
        #loggas.input_message(path = message_path, message = f'{command}')
        os.system(command)
    return 0

def ssh_connect(user,ip): #return type : ssh or 0
    logging.debug('start connect target')
    loggas.input_message(path = message_path, message = 'start connect target')
    add_known_hosts(user,ip)
    autostoring_cache_plink(user,ip)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(ip, username=user, password="", timeout=1)    # 대상IP, User명, 패스워드 입력
    try:
        logging.debug('ssh connected. %s@%s' %(user,ip))    # ssh 정상 접속 후 메시지 출력
        loggas.input_message(path = message_path, message = 'connected - %s@%s' %(user,ip))
        return ssh_client
    except Exception as err:
        logging.debug(err)    # ssh 접속 실패 시 ssh 관련 에러 메시지 출력
        loggas.input_message(path = message_path, message = 'no response from server or ip')
        return 0

def quit_ssh(ssh): #return type : 0
    ssh.close()   # ssh 접속하여 모든 작업 후 ssh 접속 close 하기
    return 0

def check_ssh_connection(ssh): #return type : bool
    if ssh == 0:
        logging.debug('ssh_status: False')
        return False
    #ui에서 상태 체크 및 False로 오면 ui버튼 비활성화 및 connection 활성화
    ssh_status = ssh.get_transport().is_active()
    #logging.debug('ssh_status: %s' %str(ssh_status))
    return ssh_status

## ============================================================
## those are functions during implementation 


def target_reset(user,ip): #return type : str, str
    logging.debug('send target reset')
    mb_data =configus.load_config(mb_path)
    command = 'ssh  -o StrictHostKeyChecking=no root@10.120.1.97 ./ifs/bin/reset'
    lines = send_by_plink(user,ip,command)
    return 0

def get_newest_trigger_number(user,ip):
    trigger_number = None
    mb_data =configus.load_config(mb_path)
    trigge_location = mb_data[mb_data['current_project']]['path_loca_trigger']
    trigge_extension = mb_data[mb_data['current_project']]['sort_trigger_list'][0]
    lines =  send_by_plink(user,ip,f'ls {trigge_location} | grep {trigge_extension}')
    if '\n' not in lines:
        return None
    #logging.info(lines)
    searched_triggers = lines.split('\n')
    #logging.info(searched_triggers)
    #find max value
    triggers = {}
    for trigger in searched_triggers:
        if len(trigger.split('_')) > 2:
            triggers[int(trigger.split('_')[1])] = trigger
    logging.info(triggers[max(triggers)])
    trigger_number = triggers[max(triggers)].split('.tar')[0]
    return trigger_number

def make_trigger(user,ip): #return type : str, str
    logging.debug('send user trigger.')
    mb_data =configus.load_config(mb_path)
    command = mb_data[mb_data['current_project']]['user_trigger']
    logging.info(command)
    lines = send_by_plink(user,ip,command)
    logging.info(lines)
    import time
    time.sleep(3)
    trigger_number = get_newest_trigger_number(user,ip)
    get_tmp_screenshot(user = user,ip=ip, server_file_path =None, download_path =config_data['last_file_path'], change_file_name =f'{trigger_number}.png')

    return lines

def partion_enlarge(user,ip): #return type : str, str
    mb_data =configus.load_config(mb_path)
    command = f"{mb_data[mb_data['current_project']]['partion_enlarge']}"
    logging.info(command)
    lines = send_by_plink(user,ip,command)
    return lines

def get_tmp_screenshot(user = 'root',ip=None, server_file_path =None, download_path ='./static/temp', change_file_name =None):  #return type : 0
    mb_data =configus.load_config(mb_path)
    if server_file_path == None:
        server_file_path = mb_data[mb_data['current_project']]['temp_png_path']
    if change_file_name is None:
        change_file_name = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    #make file path
    server_file_path = server_file_path
    local_path_downloaded = os.path.join(download_path,os.path.basename(server_file_path))
    local_path_changed = os.path.join(download_path,os.path.basename(change_file_name))
    os.remove(local_path_downloaded) if os.path.isfile(local_path_downloaded) else None
    downloaded_result, download_path = download_file(user,ip,server_file_path,download_path)
    if downloaded_result is not True:
        return 0
    else:
        #change file name
        os.rename(download_path,local_path_changed) if not os.path.isfile(local_path_changed) else None
        return 0

def get_location_from_HU ():
    return 0


def get_trigger_screenshot(folder_path):
    mb_data =configus.load_config(mb_path)
    user = mb_data['user']
    ip = mb_data['current_ip']
    error = None
    try:
        get_trigger(user,ip,folder_path=folder_path)
        extract_screenshot_from_trigger(folder_path)
    except Exception as E:
        logging.critical(traceback.format_exc())
        loggas.input_message(path = message_path, message = f'there is error on_get_user_trigger')
        loggas.input_message(path = message_path, message = f'contact the admin for more information')
        error = E
    return error

## ============================================================
## ============================================================
## those are call functions from UI 

#============================== service ============================================

def stop_navi_service():
    mb_data =configus.load_config(mb_path)
    user = mb_data['user']
    ip = mb_data['current_ip']
    send_by_plink(user,ip,mb_data[mb_data['current_project']]['stop_service'])
    return 0

def start_navi_service():
    mb_data =configus.load_config(mb_path)
    user = mb_data['user']
    ip = mb_data['current_ip']
    send_by_plink(user,ip,mb_data[mb_data['current_project']]['start_service'])
    return 0

#============================== persistancy ============================================
def reset_persis():
    mb_data =configus.load_config(mb_path)
    user = mb_data['user']
    ip = mb_data['current_ip']
    stop_navi_service()
    send_by_plink(user,ip,mb_data[mb_data['current_project']]['reset_persistency'])
    start_navi_service()
    return 0

#============================== change pos ============================================
def convert_location(url):
    #get lattitude and longtude
    locations = re.findall('-?[0-9]{1,3}\.[0-9]{5,7}',url)
    if len(locations) <2:
        return 1
    else:
        latitude = float(locations[0])
        longtude = float(locations[1])
        con_latitude = str(round(latitude*60*60*100))
        con_longtude = str(round(longtude*60*60*100))
        return latitude, longtude, con_latitude, con_longtude

def backup_navi_environment(map_evn_file):
    mb_data =configus.load_config(mb_path)
    map_evn_file_ori = map_evn_file.replace('.','_ori.')
    map_evn_file_back = map_evn_file.replace('.','_back.')

    #copy files
    check_ori_file = file_check_in_target(user=mb_data['user'],ip=mb_data['current_ip'],file = map_evn_file_ori)
    send_by_plink(user=mb_data['user'],ip=mb_data['current_ip'],command= mb_data[mb_data['current_project']]['mount_rw'])
    send_by_plink(user=mb_data['user'],ip=mb_data['current_ip'],command= f'cp {map_evn_file} {map_evn_file_ori}') if check_ori_file is False else None
    send_by_plink(user=mb_data['user'],ip=mb_data['current_ip'],command= f'cp {map_evn_file} {map_evn_file_back}')
    return 0


def update_pos_into_navi_environment(map_evn_file,url):
    mb_data =configus.load_config(mb_path)
    download_result, download_path = download_file(user=mb_data['user'],ip=mb_data['current_ip'],file=map_evn_file)
    if download_result is False:
        return False

    #replace xml file
    if download_result is True:
        logging.info(download_path)
        loca = convert_location(url)
        if loca == 1:
            return False
        else:
            logging.info(f'lati : {loca[0]} - convert {loca[2]}')
            logging.info(f'long : {loca[1]} - convert {loca[3]}')
            
            tree = xmlas.load_xml(download_path)
            current_lati = xmlas.get_txt_nv_key_value(tree,"DEFAULT_LATITUDE")
            current_long = xmlas.get_txt_nv_key_value(tree,"DEFAULT_LONGITUDE")
            logging.info(f'change DEFAULT_LATITUDE {current_lati} ->  {loca[2]} ')
            logging.info(f'change DEFAULT_LONGITUDE {current_long} ->  {loca[3]} ')
            tree = xmlas.change_txt_nv_key_value(tree,"DEFAULT_LATITUDE",loca[2])
            tree = xmlas.change_txt_nv_key_value(tree,"DEFAULT_LONGITUDE",loca[3])
            xmlas.save_xml(tree, download_path)
    #input xml into server
    usre = mb_data['user']
    ip = mb_data['current_ip']
    command = f'static\\tool\putty\pscp.exe "{download_path}" "{usre}@{ip}:{map_evn_file}"'
    os.system(command)
    send_by_plink(user=mb_data['user'],ip=mb_data['current_ip'],command= f'chown -R nav:navi {download_path} | chmod 750 {download_path}')

    #remove persistancy
    send_by_plink(user=mb_data['user'],ip=mb_data['current_ip'],command= mb_data[mb_data['current_project']]['stop_service'])
    send_by_plink(user=mb_data['user'],ip=mb_data['current_ip'],command= mb_data[mb_data['current_project']]['reset_persistancy'])
    send_by_plink(user=mb_data['user'],ip=mb_data['current_ip'],command= mb_data[mb_data['current_project']]['start_service'])
    os.remove(download_path)
    return True


def change_default_pos(url): #return type : bool
    mb_data =configus.load_config(mb_path)
    map_evn_file = mb_data[mb_data['current_project']]['map_env_path']
    
    return_value = False
    for file in map_evn_file:
        backup_navi_environment(file)
        update_value = update_pos_into_navi_environment(file,url)
        return_value = (return_value|update_value)
    return return_value
#============================== version ============================================
def get_map_version(user,ip,path = './static/temp'): #return type : str
    mb_data =configus.load_config(mb_path)
    current_project = mb_data['current_project']
    map_path = mb_data[current_project]['map_info']
    map_ver = '-'
    download_result, download_path = download_file(user,ip,map_path,path)
    if download_result == False:
        logging.info('there is no file')
        return map_ver
    if download_result == True:  
        con = sqlite3.connect(download_path)
        cur = con.cursor()
        try:
            fetch = cur.execute('select value, RegVersion from ProdStringListTable').fetchall()
            map_ver = str(fetch[0][0])+"_"+str(fetch[0][1])
        except:
            map_ver = '-'
        con.close()
        os.remove(download_path) if os.path.isfile(download_path) else 0
        return map_ver

def get_version(user,ip): #return type : map(str)
    logging.info('start get version')
    mb_data =configus.load_config(mb_path)
    current_project = mb_data['current_project']
    hu_ver = send_by_plink(user,ip,mb_data[current_project]['hu_version']).replace('\n', '').replace('\r', '')
    sw_ver = send_by_plink(user,ip,mb_data[current_project]['sw_version']).replace('\n', '').replace('\r', '')
    map_ver = send_by_plink(user,ip,mb_data[current_project]['map_version']).replace('\n', '').replace('\r', '')
    ui_ver = send_by_plink(user,ip,mb_data[current_project]['ui_version']).replace('\n', '').replace('\r', '').replace('carbon-ui', '').replace('"', '').replace(':', '')
    map_ver= get_map_version(user,ip)
    #logging.debug(f'hu_ver: {hu_ver}, sw_ver: {sw_ver} map_ver: {map_ver} ui_ver: {ui_ver}')
    return hu_ver, sw_ver, map_ver, ui_ver

#============================== traffic ============================================
def get_traffic_sdi_dat(user,ip,path='./static/temp/traffic'): #return type : int
    mb_data =configus.load_config(mb_path)
    current_project = mb_data['current_project']
    traffic_sdi_dat = mb_data[current_project]['traffic_sdi_dat']
    sdi_path = os.path.join(path,os.path.basename(traffic_sdi_dat))
    os.remove(sdi_path) if file_check_in_pc(sdi_path,path) is True else 0
    download_file(user,ip,traffic_sdi_dat,path)
    loggas.input_message(path = message_path, message = 'traffic sdi downloading done!')
    loggas.input_message(path = message_path, message = 'downloading path - %s' %path)
    return 0

#============================== binary ============================================
def get_folder_list(user,ip,path):
    cmd = f'ls -d {path}/*/'
    folders = send_by_plink(user,ip,cmd)
    #modify full path and slash
    folders = folders.replace(f'{path}','')
    folders = folders.replace('/','')
    #change to list
    folders = folders.split('\n')
    folders.remove('')
    #logging.info(folders)
    return folders


def change_binary(user,ip,version):
    mb_data =configus.load_config(mb_path)
    current_project = mb_data['current_project']
    send_by_plink(user,ip, mb_data[current_project]['stop_service'])
    send_by_plink(user,ip, mb_data[current_project]['remove_binary'])
    send_by_plink(user,ip, f'cp {mb_data[current_project]["location_binary"]}/{version}/* {mb_data[current_project]["location_binary"]}')
    send_by_plink(user,ip, mb_data[current_project]['permisson_binary'])
    send_by_plink(user,ip, mb_data[current_project]['start_service'])
    return 0

#============================== trigger ============================================

def extract_lz4(file_path='./static/temp/trigger'): #return type : int
    #check lz4 already decompress.
    if os.path.exists(file_path[:-4]) is True:
        logging.info(f'file already exist - {file_path}')
        return 0 
    lz4_path = 'static\lz4_win64_v1_9_4\lz4.exe'
    command = '%s -frm "%s"' %(lz4_path,file_path)
    logging.info(command)
    os.system(command)
    return 0

def extract_png_from_tar(file_path='static/temp/trigger'): #return type : int
    command = 'tar -xvf "%s" -C "%s" *.png' %(file_path,os.path.dirname(os.path.abspath(file_path)))
    logging.info(command)
    os.system(command)
    return 0

def get_trigger(user,ip,folder_path='./static/temp/trigger'): #return type : int
    loggas.input_message(path = message_path, message = 'trigger downloading start!')
    mb_data =configus.load_config(mb_path)
    current_project = mb_data['current_project']
    trigger_path = mb_data[current_project]['path_loca_trigger']
    sort_trigger_list = mb_data[current_project]['sort_trigger_list']
    trigger_lines = send_by_plink(user,ip, f'ls {trigger_path}')
    str_today = datetime.date.today().strftime("%Y%m%d")
    trigger_list = trigger_lines.split('\n')
    #logging.info(trigger_list)
    #logging.info(sort_trigger_list)
    sorted_trigger_list = [trigger for trigger in trigger_list if any(xs in trigger for xs in sort_trigger_list)]
    #logging.info(sorted_trigger_list)

    for trigger_file_name in sorted_trigger_list:
        if str_today in trigger_file_name:
            logging.info(f'downloading {trigger_file_name}')
            trigger_file_path = f"{trigger_path}/{trigger_file_name}"
            download_file(user,ip,trigger_file_path,path=folder_path)
        else:
            pass
    logging.info('trigger downloading done!')
    loggas.input_message(path = message_path, message = 'trigger downloading done!')
    loggas.input_message(path = message_path, message = f'downloading path - {folder_path}')
    return 0


def extract_screenshot_from_trigger(trigger_folder_path='./static/temp/trigger'): #return type : int
    logging.info(trigger_folder_path)
    loggas.input_message(path = message_path, message = 'start to extract screenshot from HU done!')
        
    #extraf tar from lz4
    files = os.listdir(trigger_folder_path)
    for file in files:
        if str(file).split('.')[-1] == 'lz4':
            extract_lz4('%s/%s' %(trigger_folder_path,file))
    logging.info('tar from lz4 done.')
   
    #extraf png from tar
    files = os.listdir(trigger_folder_path)
    for file in files:
        if str(file).split('.')[-1] == 'tar':
            extract_png_from_tar('%s/%s' %(trigger_folder_path,file))
    logging.info('png from tar done.')

    #move png to path and lz4 into subfolder.
    logging.info(os.path.join(trigger_folder_path,'lz4'))
    os.mkdir(os.path.join(trigger_folder_path,'lz4')) if not os.path.exists(os.path.join(trigger_folder_path,'lz4')) else None
    for root, dirs, files in os.walk(trigger_folder_path):
        for file in files:
            logging.info(file)
            if file.endswith(".png"):
                os.replace(os.path.join(root, file),os.path.join(trigger_folder_path, file))
            if file.endswith(".lz4"):
                #print(os.path.join(root, file),os.path.join(trigger_folder_path,'lz4', file))
                #os.replace(os.path.join(root, file),os.path.join(trigger_folder_path,'lz4', file))
                pass
            if file.endswith(".json"):
                os.replace(os.path.join(root, file),os.path.join(trigger_folder_path,'lz4', file))

    # remove screenshot folder.
    onlyfolders = [f for f in os.listdir(trigger_folder_path) if not os.path.isfile(os.path.join(trigger_folder_path, f))]
    for onlyfor in onlyfolders:
        if 'trigger' in onlyfor:
            logging.info(onlyfor)
            shutil.rmtree(os.path.join(trigger_folder_path,onlyfor))
    logging.info('extract screenshot from HU done!')
    loggas.input_message(path = message_path, message = 'extract screenshot from HU done!')
    loggas.input_message(path = message_path, message = 'downloading path - %s' %trigger_folder_path)
    return 0


if __name__ == "__main__":
    logging.info(__name__)
    loggas.input_message(path = message_path, message = __name__)