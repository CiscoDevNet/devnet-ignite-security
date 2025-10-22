# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : get an incident and every of it's details ( sightings, indicators, relationships )
'''
import requests
import json
import sys
from datetime import datetime, date, timedelta
from crayons import *
from functions_for_xdr_asking_for_a_token import *
import env as env


#  def_get_incident_details***
def get_incident_details(incident_id):
    '''
    MODIFIED : 2025-07-30
    description : get the incident JSON payload from the XDR thanks to the Conure API
    
    how_to_call_it : incident_file_name=get_incident_details(incident_id)
    '''
    route="/get_incident_details"
    env.level+='-'
    print('\n'+env.level,white('def get_incident_details() in get_incident_details.py : >\n',bold=True))
    print('\nincident_id : ',incident_id+'\n')
    print(cyan('-> Let\'s get API credentials\n',bold=True)) 
    with open('config.txt','r') as file:
        text_content=file.read()
    client_id,client_password,host_for_token,host,conure = parse_config(text_content) # parse config.txt
    fa = open("ctr_token.txt", "r")
    access_token = fa.readline()
    fa.close()
    test_tenant=check_cnx_to_tenant(host_for_token,access_token)
    if test_tenant==401:
        print(red('Wrong Token',bold=True))
        access_token=ask_for_a_token()
    # save the incident summary get from conure API call
    file_name='./incident-details-'+current_date_and_time()+'.json'
    print('\n file_name out :',yellow(file_name,bold=True))
    fb = open(file_name, "w")
    headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}  
    #CONURE API
    # ############################################################################################################################################################################
    #
    # API documentation at :  https://developer.cisco.com/docs/cisco-xdr/private-intelligence-api-incident-search-for-incident-entities-using-a-es-query-syntax-and-field-filters/    
    #
    # ############################################################################################################################################################################
    with open('config.txt','r') as file:
        text_content=file.read()
    client_id,client_password,host_for_token,host,conure = parse_config(text_content)
    url=f"{conure}/v2/incident/{incident_id}/export"
    print(cyan('\nURL :'+url+'\n',bold=True))
    print(magenta('\n--> CALL  A SUB FUNCTION : get call to CONURE API ',bold=True)) 
    response = requests.get(url, headers=headers) # API GET CALL to XDR       
    print('\n response.status_code :',yellow(response.status_code,bold=True))   
    if response.status_code==401: # wrong token, it probable expired
        access_token=get_ctr_token(host_for_token,client_id,client_password)
        headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
        print(magenta('\n--> CALL  A SUB FUNCTION try again : get call to CONURE API ',bold=True))
        response = requests.get(url, headers=headers)
        payload = json.dumps(response.json(),indent=4,sort_keys=True, separators=(',', ': '))
        print(cyan('\n'+payload,bold=True))
        if response.status_code==200:
            fb.write(payload)
            fb.close()
            result=1
        else:
            result=0
    elif response.status_code==404: # incident not found
        print(red('\n--> Incident not found ',bold=True))
        result=0
    else:
        payload = json.dumps(response.json(),indent=4,sort_keys=True, separators=(',', ': '))
        # here under save the result into a text file
        fb.write(payload)
        fb.close()
        result=1
    env.level=env.level[:-1]
    return file_name,result
    

#  def_current_date_and_time***
def current_date_and_time():
    '''
    MODIFIED : 2025-07-20

    description : get current date and time in the YYYYmmddHMSformat
    '''
    route="/current_date_and_time"
    env.level+='-'
    print('\n'+env.level,white('def current_date_and_time() in get_incident_details.py : >\n',bold=True))
    current_time = datetime.utcnow()
    timestampStr = current_time.strftime("%Y%m%d%H%M%S")
    env.level=env.level[:-1]
    return(timestampStr)
    
if __name__=="__main__":
    print("start here")
    with open('./incident_id.txt') as file:        
        incident_id=file.read()
    print()    
    incident_file_name,result=get_incident_details(incident_id)
    if result==1:
        print(green(f"\nOK DONE  - Result in : {incident_file_name}",bold=True))
    else:
        print(red(f"\nOK DONE  - ERROR : {incident_file_name}",bold=True))
        
