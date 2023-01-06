# -*- coding: utf-8 -*-
#!/usr/bin/python
import os
import datetime
import paramiko

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

ip_list = mb_data['ip_list']
user = mb_data['user']

def ssh_connect():
    logging.debug('start')
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(ip_list[1], username=user, password="")    # 대상IP, User명, 패스워드 입력
        logging.debug('ssh connected. %s@%s' %(user,str(ip_list[1])))    # ssh 정상 접속 후 메시지 출력
        logging.debug('send user trigger.')    # ssh 정상 접속 후 메시지 출력
        ssh.exec_command(mb_data['user_trigger'])
        ssh.close()   # ssh 접속하여 모든 작업 후 ssh 접속 close 하기
    except Exception as err:
        logging.debug(err)    # ssh 접속 실패 시 ssh 관련 에러 메시지 출력

def send(ssh):
    stdin, stdout, stderr = ssh.exec_command("ls -l")   # ssh 접속한 경로에 디렉토리 및 파일 리스트 확인 명령어 실행
    lines = stdout.readlines()
    for i in lines:    # for문을 통해 명령어 결과값 출력.
        re = str(i).replace('\n', '')
        print(re)

if __name__ == "__main__":
    logging.info(__name__)
    logging_message.input_message(path = message_path, message = __name__)