# -*- coding: utf-8 -*-
#!/usr/bin/python
import sqlite3
import paramiko
import os
import datetime
import shutil
import re

#add internal libary
from _src._api import logger, config, logging_message

    
#make logpath
logging= logger.logger

#loading config data
config_path = 'static\config\config.json'
config_data =config.load_config(config_path)
qss_path = config_data['qss_path']
message_path = config_data['message_path']
test_cycle_url = config_data['test_cycle_url']

mb_path = 'static\config\mb_command.json'
mb_data =config.load_config(mb_path)

user = mb_data['user']
ip = mb_data['ip']
current_project = mb_data['current_project']

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
    stdin, stdout, stderr = ssh.exec_command(command)   # ssh 접속한 경로에 디렉토리 및 파일 리스트 확인 명령어 실행
    lines = stdout.readlines()
    temp_line =''
    for line in lines:
        #logging.debug(line)
        temp_line = temp_line + line
    return temp_line 

def send_by_plink(user,ip,command): #return type : str
    command = f'static\\tool\putty\plink.exe {user}@{ip} "{command}" > static\\temp\plink.txt'
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
        logging.info(f'file_in_target: {file_in_target}') if file_in_target == False else None
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
        #logging_message.input_message(path = message_path, message = f'{command}')
        os.system(command)
    return 0

def ssh_connect(user,ip): #return type : 0
    logging.debug('start connect target')
    logging_message.input_message(path = message_path, message = 'start connect target')
    autostoring_cache_plink(user,ip)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    try:
        ssh.connect(ip, username=user, password="", timeout=3)    # 대상IP, User명, 패스워드 입력
        logging.debug('ssh connected. %s@%s' %(user,ip))    # ssh 정상 접속 후 메시지 출력
        logging_message.input_message(path = message_path, message = 'connected - %s@%s' %(user,ip))
        return ssh
    except Exception as err:
        logging.debug(err)    # ssh 접속 실패 시 ssh 관련 에러 메시지 출력
        logging_message.input_message(path = message_path, message = 'no response from server or ip')
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

def make_trigger(user,ip): #return type : time, str
    logging.debug('send user trigger.')
    command = mb_data[current_project]['user_trigger']
    logging.info(command)
    lines = send_by_plink(user,ip,command)
    now = datetime.datetime.now()
    logging.info(lines)
    #for line in lines:    # for문을 통해 명령어 결과값 출력.
    #    re = str(line).replace('\n', '')
    #    logging_message.input_message(path = message_path, message = re)
    return now, lines
    

def get_tmp_screenshot(user = 'root',ip=None,file='/tmp/eel-screenshot.png.png',path='./static/temp',trigger_time=None):  #return type : 0
    download_result, download_path = download_file(user,ip,file,path)
    if download_result is not True:
        return 0
    if trigger_time is None:
        now_time = str(datetime.datetime.now())
        trigger_time = str(now_time).replace(' ','_').replace(':','_')
    else:
        trigger_time = str(trigger_time).replace(' ','_').replace(':','_')
        download_path = f'{path}/{os.path.basename(file)}'
        change_path = f'{path}/screenshot_{trigger_time}_.png'
        #os.system(f'rename "{download_path}" "{change_path}"')
        os.rename(download_path,change_path)
        return 0


## ============================================================
## ============================================================
## those are call functions from UI 

#============================== version ============================================
def get_map_version(user,ip,path = './static/temp'): #return type : str
    map_path = mb_data[current_project]['dbpath']
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
    hu_ver = send_by_plink(user,ip,mb_data[current_project]['hu_version']).replace('\n', '').replace('\r', '')
    sw_ver = send_by_plink(user,ip,mb_data[current_project]['sw_version']).replace('\n', '').replace('\r', '')
    map_ver = send_by_plink(user,ip,mb_data[current_project]['map_version']).replace('\n', '').replace('\r', '')
    ui_ver = send_by_plink(user,ip,mb_data[current_project]['ui_version']).replace('\n', '').replace('\r', '').replace('carbon-ui', '').replace('"', '').replace(':', '')
    map_ver= get_map_version(user,ip)
    logging.debug(f'hu_ver: {hu_ver}, sw_ver: {sw_ver} map_ver: {map_ver} ui_ver: {ui_ver}')
    return hu_ver, sw_ver, map_ver, ui_ver

#============================== traffic ============================================
def get_traffic_sdi_dat(user,ip,path='./static/temp/traffic'): #return type : int
    traffic_sdi_dat = mb_data[current_project]['traffic_sdi_dat']
    sdi_path = os.path.join(path,os.path.basename(traffic_sdi_dat))
    os.remove(sdi_path) if file_check_in_pc(sdi_path,path) is True else 0
    download_file(user,ip,traffic_sdi_dat,path)
    logging_message.input_message(path = message_path, message = 'traffic sdi downloading done!')
    logging_message.input_message(path = message_path, message = 'downloading path - %s' %path)
    return 0

#============================== binary ============================================
def change_binary(user,ip,path_pc):
    autostoring_cache_plink(user,ip)
    #check binary exist
    filelist = os.listdir(path_pc)
    if 'nv_main' not in filelist:
        logging.info(f'there is no navi binary')
        logging_message.input_message(path = message_path, message = f'there is no navi binary')
        return 0
    #how to change binary
    logging_message.input_message(path = message_path, message = f'start change binary')
    commands = mb_data[current_project]['change_binary']
    #following the step.
    for commd in commands:
        commds = commd.split(' - ')
        if commds[0] == 'commnd':
            send_by_plink(user,ip,commds[1])
        if commds[0] == 'copy_new_binary':
            for fi in filelist:
                uploadfile(user,ip,os.path.join(path_pc,fi),commds[1])    
            #need file check -> no problme = pass / else -> break and return 0
            logging.info(os.path.getsize(path_pc))
        if commds[0] == 'change_new_binary':
            send_by_plink(user,ip,commds[1])
    logging_message.input_message(path = message_path, message = f'change binary done.')
    return 0

#============================== trigger ============================================
def get_trigger(user,ip,folder_path='./static/temp/trigger'): #return type : int
    logging_message.input_message(path = message_path, message = 'trigger downloading start!')
    trigger_path =mb_data[current_project]['path_loca_trigger']
    trigger_lines = send_by_plink(user,ip, f'ls {trigger_path}')
    str_today = datetime.date.today().strftime("%Y%m%d")
    #logging.info(trigger_lines.split('\n'))
    #logging.info(str_today)
    for trigger_file_name in trigger_lines.split('\n'):
        hu_date = re.findall('[0-9]{8}',trigger_file_name)[0] if len(re.findall('[0-9]{8}',trigger_file_name)) == 1 else None
        #logging.info(hu_date)
        if hu_date == None or str_today > hu_date:
            logging.info(f'str_today - {str_today}, hu_date - {hu_date}')
        else:
            logging.info(f'downloading {trigger_file_name}')
            trigger_file_path = f"{trigger_path}/{trigger_file_name}"
            download_file(user,ip,trigger_file_path,path=folder_path)
    logging.info('trigger downloading done!')
    logging_message.input_message(path = message_path, message = 'trigger downloading done!')
    logging_message.input_message(path = message_path, message = f'downloading path - {folder_path}')
    return 0


def extract_screenshot_from_trigger(trigger_folder_path='./static/temp/trigger'): #return type : int
    logging.info(trigger_folder_path)
    logging_message.input_message(path = message_path, message = 'start to extract screenshot from HU done!')
    
    def extract_png_from_tar(file_path='static/temp/trigger'): #return type : int
        command = 'tar -xvf "%s" -C "%s" *.png' %(file_path,os.path.dirname(os.path.abspath(file_path)))
        logging.info(command)
        os.system(command)
        return 0
    
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
    logging_message.input_message(path = message_path, message = 'extract screenshot from HU done!')
    logging_message.input_message(path = message_path, message = 'downloading path - %s' %trigger_folder_path)
    return 0



if __name__ == "__main__":
    logging.info(__name__)
    logging_message.input_message(path = message_path, message = __name__)