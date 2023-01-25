# -*- coding: utf-8 -*-
#!/usr/bin/python
import sqlite3
import paramiko
import os

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

ip = mb_data['ip']
user = mb_data['user']
current_project = mb_data['current_project']

def add_known_hosts(user,ip):
    os.system('del %s' %os.path.join(os.path.expanduser('~'),'.ssh','known_hosts'))
    command = 'ssh -o StrictHostKeyChecking=no %s@%s echo -n' %(user,ip)
    os.system(command)
    return 0

def download_file(user,ip,file,path='./static/temp'):
    add_known_hosts(user,ip)
    command = 'scp -q "%s@%s:%s" "%s"' %(user,ip,file,path)
    os.system(command)
    logging.debug(command)
    download_path = os.path.join(path,os.path.basename(file))
    return download_path

def ssh_connect(ip,user):
    logging.debug('ssh connection start')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    try:
        ssh.connect(ip, username=user, password="", timeout=10)    # 대상IP, User명, 패스워드 입력
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
    for i in lines:    # for문을 통해 명령어 결과값 출력.
        re = str(i).replace('\n', '')
        logging.debug(re)

def make_trigger(ssh):
    logging.debug('send user trigger.')
    stdin, stdout, stderr = ssh.exec_command(mb_data[current_project]['user_trigger'])
    lines = stdout.readlines()
    for line in lines:    # for문을 통해 명령어 결과값 출력.
        re = str(line).replace('\n', '')
        logging_message.input_message(path = message_path, message = re)
    return 0

def get_map_version():
    file = config_data['dbpath']
    ip = mb_data['ip']
    user = mb_data['user']
    path = './static/temp'
    downlaod_file_path = download_file(user,ip,file,path)
    con = sqlite3.connect(downlaod_file_path)
    cur = con.cursor()
    fetch = cur.execute('select value, RegVersion from ProdStringListTable').fetchall()
    map_ver = str(fetch[0][0])+"_"+str(fetch[0][1])
    con.close()
    os.system('del "%s"' %downlaod_file_path)
    return map_ver

def get_version(ssh):
    def get_each_version(command):
        ver = ''
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        for i in lines:
            re = str(i).replace('\n', '').replace('\r', '')
            ver = ver+re
        return ver
    hu_ver = get_each_version(mb_data[current_project]['hu_version'])
    sw_ver = get_each_version(mb_data[current_project]['sw_version'])
    map_ver = get_each_version(mb_data[current_project]['map_version'])
    ui_ver = get_each_version(mb_data[current_project]['ui_version'])
    #logging.debug(hu_ver)
    #logging.debug(sw_ver)
    #logging.debug(map_ver)
    #logging.debug(ui_ver)
    return hu_ver, sw_ver, map_ver, ui_ver


if __name__ == "__main__":
    logging.info(__name__)
    logging_message.input_message(path = message_path, message = __name__)