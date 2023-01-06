# -*- coding: utf-8 -*-
#!/usr/bin/python
import os
import datetime

#add internal libary
from _src._api import logger, excel, playload, config, logging_message

    
#make logpath
logging= logger.logger

#loading config data
config_path = 'static\config\config.json'
config_data =config.load_config(config_path)
qss_path = config_data['qss_path']
message_path = config_data['message_path']
test_cycle_url = config_data['test_cycle_url']

def make_excel_data(data,ws_list):
    tc_data ={}
    for row_index in ws_list:
        tc_data[str(row_index)] = str(data[ws_list.index(row_index)].value)
        tc_data['updateDefectList'] = 'true'
    return tc_data

def update_test_execution_by_rest(rh, execution_data):
    #logging.info('%s' %(str(execution_data)))
    tc_playload = {}
    execution_data['ExecutionStatus'] = config_data['test_resut'][execution_data['ExecutionStatus']]
    #logging.info('%s' %(str(execution_data)))

    input_items_for_test_cycle = config_data['input_items_for_test_cycle']
    for input_item_for_test_cycle in input_items_for_test_cycle:
        input_item_for_test_cycle = str(input_items_for_test_cycle[input_item_for_test_cycle]).replace('field_input_value',execution_data[input_item_for_test_cycle]).replace('\n','\\n')
        input_item_for_test_cycle = eval(input_item_for_test_cycle)
        tc_playload.update(input_item_for_test_cycle['input_playload'])
    tc_playload['defectList'] = tc_playload['defectList'].split(',')
    logging.info('test result infomation - %s' %str(tc_playload))
    logging_message.input_message(path = message_path,message = 'test result infomation - %s' %str(tc_playload))
    result = rh.updateExecution(execution_data['ExecutionId'],playload.makeplayload(tc_playload))
    if result.status_code != '200':
        logging.info(result.status_code)
        logging_message.input_message(path = message_path,message = 'test execution updated - %s' %str(execution_data['ExecutionId']))
    else:
        logging.info(result.text)
        logging.info(result)
        logging_message.input_message(path = message_path,message = 'test execution updated error - %s - %s' %(str(execution_data['ExecutionId']),result.text))
    return 0

def update_test_cycle(rh, file):
    # init
    logging.info('start importing test cycle - %s' %file)
    logging_message.input_message(path = message_path,message = 'start importing test cycle - %s' %file)
    wb = excel.Workbook(file,read_only=True,data_only=True)
    logging.info(wb.get_sheet_list())
    worksheet = config_data['worksheet']
    logging.info('search for %s in %s' %(worksheet,str(wb.get_sheet_list())))
    logging_message.input_message(path = message_path,message = 'search for %s in %s' %(worksheet,str(wb.get_sheet_list())))
    if worksheet not in wb.get_sheet_list():
        logging.info('there is no %s in %s so use first sheet' %(worksheet,str(wb.get_sheet_list())))
        logging_message.input_message(path = message_path,message = 'there is no %s in %s so use first sheet' %(worksheet,str(wb.get_sheet_list())))
        worksheet = wb.get_sheet_list()[0]
        config_data['worksheet'] = worksheet
        config.save_config(config_data,config_path)
    else:
        logging.info('there is %s in %s so use the sheet' %(worksheet,str(wb.get_sheet_list())))
        logging_message.input_message(path = message_path,message = 'there is %s in %s so use the sheet' %(worksheet,str(wb.get_sheet_list())))
    tc_ws = wb.get_worksheet(worksheet)
    tc_row_index = wb.get_first_row(worksheet)
    input_items_tc = config_data['input_items_for_test_cycle']
    logging.info('check row index - %s' %str(tc_row_index))

    logging.info('this is input items for test cycle %s' %input_items_tc.keys())

    for data in tc_ws.rows:
        tc_data = {}
        tc_data = make_excel_data(data,tc_row_index)
        #if first cell is None => break
        ExecutionId = tc_data['ExecutionId']
        StepId = tc_data['StepId'] if 'StepId' in tc_data.keys() else None
        if ExecutionId == 'ExecutionId':
            continue
        if ExecutionId in ('None',None):
            break
        else:
            logging_message.input_message(path = message_path,message = 'ExecutionId %s - StepId %s' %(ExecutionId,StepId))
            logging.info('ExecutionId %s - StepId %s' %(ExecutionId,StepId))
            update_test_execution_by_rest(rh, tc_data)
    logging_message.input_message(path = message_path,message ='import done and close workbook!')
    logging.info('import done and close workbook!')
    wb.close_workbook()
    return 0
    