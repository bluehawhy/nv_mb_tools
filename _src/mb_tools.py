# -*- coding: utf-8 -*-
#!/usr/bin/python
import sqlite3
import paramiko
import os
import datetime
import shutil

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
def add_known_hosts(user,ip):
    os.system('del %s' %os.path.join(os.path.expanduser('~'),'.ssh','known_hosts'))
    command = 'ssh -o StrictHostKeyChecking=no %s@%s echo -n' %(user,ip)
    os.system(command)
    return 0

def file_check_via_ssh(ssh=None,file=None):
    command = f'ls {file}'
    check_value = False
    if ssh==None:
        logging.info('need to connect ssh')
    else:
        filelists = send(ssh,command)
        check_value = True if len(filelists) > 0 else False
    return check_value
    
def file_check_via_console(user,ip,file):
    command = f'ssh {user}@{ip} ls {file}'
    check_value = False
    logging.info(command)
    return check_value

def get_tmp_screenshot(user = 'root',ip=None,file='/tmp/eel-screenshot.png.png',path='./static/temp',time=None):
    command = 'scp -q "%s@%s:%s" "%s"' %(user,ip,file,path)
    os.system(command)
    if time is None:
        time = str(datetime.datetime.now())
    time = str(time).replace(' ','_').replace(':','_')
    download_path = f'{path}/{os.path.basename(file)}'
    change_path = f'{path}/screenshot_{time}_.png'
    #os.system(f'rename "{download_path}" "{change_path}"')
    os.rename(download_path,change_path)
    return 0

def download_file(ssh,user,ip,file,path='./static/temp'):
    loca_file_path = os.path.join(path,os.path.basename(file))
    if os.path.exists(loca_file_path) is True:
        logging.info(f'file already exist - {loca_file_path}')
        return True
    #check file exist.
    check_value = file_check_via_ssh(ssh,file)
    #logging.info(check_value)
    if check_value is True:
        command = 'scp -q "%s@%s:%s" "%s"' %(user,ip,file,path)
        os.system(command)
        download_path = os.path.join(path,os.path.basename(file))
        return download_path
    else:
        logging.info('no file in target - %s/%s' %(path,os.path.basename(file)))
        return False

def uploadfile(user,ip,path_pc,path_target):
    command = f'scp -q {path_pc} {user}@{ip}:{path_target}'
    logging.info(command)
    logging_message.input_message(path = message_path, message = f'upload {path_pc} into {user}@{ip}:{path_target}')
    os.system(command)
    return 0

def ssh_connect(ip,user):
    logging.debug('ssh connection start')
    add_known_hosts(user,ip)
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

def quit_ssh(ssh):
    ssh.close()   # ssh 접속하여 모든 작업 후 ssh 접속 close 하기
    return 0

def check_ssh_connection(ssh):
    if ssh == 0:
        logging.debug('ssh_status: False')
        return False
    #ui에서 상태 체크 및 False로 오면 ui버튼 비활성화 및 connection 활성화
    ssh_status = ssh.get_transport().is_active()
    #logging.debug('ssh_status: %s' %str(ssh_status))
    return ssh_status

def send(ssh,command):
    stdin, stdout, stderr = ssh.exec_command(command)   # ssh 접속한 경로에 디렉토리 및 파일 리스트 확인 명령어 실행
    lines = stdout.readlines()
    #for line in lines:
    #    logging.debug(line)
    return lines

## ============================================================

## ============================================================
## ============================================================
## those are call functions from UI 
def change_binary(user,ip,path_pc):
    #check binary exist
    filelist = os.listdir(path_pc)
    if 'nv_main' not in filelist:
        logging.info(f'there is no navi binary')
        logging_message.input_message(path = message_path, message = f'there is no navi binary')
        return 0
    #how to change binary
    logging_message.input_message(path = message_path, message = f'start change binary')
    commands = mb_data[current_project]['change_binary']
    for commd in commands:
        if "copy new sw" not in commd:
            cmd = f'ssh {user}@{ip} "{commd}"'
            logging.info(f'send command {cmd}')
            os.system(cmd)
        else:
            logging.info(f'start copy binary{commd}')
            path_target = commd.split("'")[-2]
            logging.info(f'target path = {path_target}')
            for navi_bi in filelist:
                pc_file_path = os.path.join(path_pc,navi_bi)
                uploadfile(user,ip,pc_file_path,path_target)
    logging_message.input_message(path = message_path, message = f'change binary done.')
    return 0

def make_trigger(ssh):
    logging.debug('send user trigger.')
    stdin, stdout, stderr = ssh.exec_command(mb_data[current_project]['user_trigger'])
    lines = stdout.readlines()
    now = datetime.datetime.now()
    for line in lines:    # for문을 통해 명령어 결과값 출력.
        re = str(line).replace('\n', '')
        logging_message.input_message(path = message_path, message = re)
    return now, lines



def get_version(ssh):
    logging.info('start get version')
    def get_each_version(command):
        ver = ''
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        for i in lines:
            re = str(i).replace('\n', '').replace('\r', '')
            ver = ver+re
        return ver

    def get_map_version(ssh,user,ip):
        map_path = mb_data[current_project]['dbpath']
        path = './static/temp'
        downlaod_file_path = download_file(ssh,user,ip,map_path,path)
        if downlaod_file_path == False:
            logging.info('there is no file')
            return '-'
        if downlaod_file_path == True:
            del_file_path = os.path.join(path,os.path.basename(map_path))
            logging.info(del_file_path)
            os.remove(del_file_path)
            downlaod_file_path = download_file(ssh,user,ip,map_path,path)
        if downlaod_file_path != 0:    
            con = sqlite3.connect(downlaod_file_path)
            cur = con.cursor()
            try:
                fetch = cur.execute('select value, RegVersion from ProdStringListTable').fetchall()
                map_ver = str(fetch[0][0])+"_"+str(fetch[0][1])
            except:
                map_ver = '-'
            con.close()
            os.remove(downlaod_file_path)
            return map_ver
    hu_ver = get_each_version(mb_data[current_project]['hu_version'])
    sw_ver = get_each_version(mb_data[current_project]['sw_version'])
    map_ver = get_each_version(mb_data[current_project]['map_version'])
    ui_ver = get_each_version(mb_data[current_project]['ui_version'])
    map_ver= get_map_version(ssh, user,ip)
    #logging.debug(hu_ver)
    #logging.debug(sw_ver)
    #logging.debug(map_ver)
    #logging.debug(ui_ver)
    return hu_ver, sw_ver, map_ver, ui_ver

def download_trigger(ssh,folder_path='./static/temp/trigger'):
    trigger_path =mb_data[current_project]['path_loca_trigger']
    ip = mb_data['ip']
    logging.info(trigger_path)
    trigger_lines = send(ssh,'ls %s' %trigger_path)
    str_today = datetime.date.today().strftime("%Y%m%d")
    #logging.info(str_today)
    for li in trigger_lines:
        trigger_file_name = str(li).replace('\n', '').replace('\r', '')
        if len(trigger_file_name.split("_")) > 3 and trigger_file_name.split("_")[2] == "HU" and trigger_file_name.split("_")[3] >= str_today:
            trigger_file_path = "%s/%s" %(trigger_path,trigger_file_name)
            logging.info('downloading %s' %trigger_file_name)
            logging_message.input_message(path = message_path, message = 'downloading %s' %trigger_file_name)
            download_file(ssh,user,ip,trigger_file_path,path=folder_path)
    logging.info('trigger downloading done!')
    logging_message.input_message(path = message_path, message = 'trigger downloading done!')
    logging_message.input_message(path = message_path, message = 'downloading path - %s' %folder_path)

    return 0


def extract_png_from_tar(file_path='./static/temp/trigger'):
    command = 'tar -xvf "%s" -C "%s" *.png' %(file_path,os.path.dirname(os.path.abspath(file_path)))
    logging.info(command)
    os.system(command)
    return 0

def extract_lz4(file_path='./static/temp/trigger'):
    #check lz4 already decompress.
    if os.path.exists(file_path[:-4]) is True:
        logging.info(f'file already exist - {file_path}')
        return 0 
    lz4_path = 'static\lz4_win64_v1_9_4\lz4.exe'
    command = '%s -frm "%s"' %(lz4_path,file_path)
    logging.info(command)
    os.system(command)
    return 0

def extract_screenshot_from_trigger(trigger_folder_path='./static/temp/trigger'):
    logging.info(trigger_folder_path)
    logging_message.input_message(path = message_path, message = 'start to extract screenshot from HU done!')
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
    
def get_traffic_sdi_dat(ssh,user,ip,traffic_sdi_dat,path='./static/temp/traffic'):
    
    if os.path.exists('%s/%s' %(path,os.path.basename(traffic_sdi_dat))) is True:
        os.remove('%s/%s' %(path,os.path.basename(traffic_sdi_dat)))
    download_file(ssh,user,ip,traffic_sdi_dat,path)
    logging_message.input_message(path = message_path, message = 'traffic sdi downloading done!')
    logging_message.input_message(path = message_path, message = 'downloading path - %s' %path)
    return 0



if __name__ == "__main__":
    logging.info(__name__)
    logging_message.input_message(path = message_path, message = __name__)