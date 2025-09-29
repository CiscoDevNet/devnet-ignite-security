# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : set_of_script to use as resources in other script for asking for an API authentication token
'''
import requests
import json
from crayons import *
import os
import sys
import env as env


#  def_parse_config***
def parse_config(text_content):
    '''
    MODIFIED : 2025-07-30
    description : read the config.txt file where are stored the XDR client details and credentials
    
    how to call it : client_id,client_password,host_for_token,host,conure = parse_config(text_content) 
    '''
    route="/parse_config"
    env.level+='-'
    print('\n'+env.level,white('def parse_config() in functions_for_xdr_asking_for_a_token.py : >\n',bold=True))
    text_lines=text_content.split('\n')
    conf_result=['','','','','']
    for line in text_lines:
        #print(green(line+'\n',bold=True))
        if 'ctr_client_id' in line:
            words=line.split('=')
            if len(words)==2:
                conf_result[0]=line.split('=')[1]
                conf_result[0]=conf_result[0].replace('"','')
                conf_result[0]=conf_result[0].replace("'","")
                conf_result[0]=conf_result[0].strip()
            else:
                conf_result[0]=""
        elif 'ctr_client_password' in line:
            words=line.split('=')
            if len(words)==2:
                conf_result[1]=line.split('=')[1]
                conf_result[1]=conf_result[1].replace('"','')
                conf_result[1]=conf_result[1].replace("'","")
                conf_result[1]=conf_result[1].strip()
            else:
                conf_result[1]=""
        elif '.eu.amp.cisco.com' in line:
            conf_result[2]="https://visibility.eu.amp.cisco.com"
            conf_result[3]="https://private.intel.eu.amp.cisco.com"
        elif '.intel.amp.cisco.com' in line:
            conf_result[2]="https://visibility.amp.cisco.com"
            conf_result[3]="https://private.intel.amp.cisco.com"
        elif '.apjc.amp.cisco.com' in line:
            conf_result[2]="https://visibility.apjc.amp.cisco.com"
            conf_result[3]="https://private.intel.apjc.amp.cisco.com"
        elif 'conure' in line:
            words=line.split('=')
            if len(words)==2:
                conf_result[4]=line.split('=')[1]
                conf_result[4]=conf_result[4].replace('"','')
                conf_result[4]=conf_result[4].replace("'","")
                conf_result[4]=conf_result[4].strip()
            else:
                conf_result[1]=""
    #print(yellow(conf_result))
    return conf_result
  

#  def_get_ctr_token***
def get_ctr_token(host_for_token,ctr_client_id,ctr_client_password):
    '''
    MODIFIED : 2025-09-10
    description : asking for an API Token to XDR
    '''
    route="/get_ctr_token"
    env.level+='-'
    print('\n'+env.level,white('def get_ctr_token() in functions_for_xdr_asking_for_a_token.py : >\n',bold=True))
    print(yellow('Asking for new CTR token\n',bold=True))
    # #########################################################################################################################
    #
    # API documentation : https://developer.cisco.com/docs/cisco-xdr/generate-access-and-refresh-tokens/
    #
    # #########################################################################################################################     
    url = f'{host_for_token}/iroh/oauth2/token'
    print('\n url :',url)   
    headers = {'Content-Type':'application/x-www-form-urlencoded', 'Accept':'application/json'}
    payload = {'grant_type':'client_credentials'}
    #print('\nctr_client_id : ',green(ctr_client_id,bold=True))
    #print('\nctr_client_password : ',green(ctr_client_password,bold=True))
    response = requests.post(url, headers=headers, auth=(ctr_client_id, ctr_client_password), data=payload) # POST CALL to XDR
    print('response =\n',cyan(response.json(),bold=True))
    if 'error' in response.json().keys():
        if response.json()['error']=='invalid_client':
            print(red('\nError Invalid client-ID !',bold=True))
            sys.exit()
        elif response.json()['error']=='wrong_client_creds':
            print(red('\nError Invalid client-Password !',bold=True))
            sys.exit()
    # here under let s extract the token
    reponse_list=response.text.split('","')
    token=reponse_list[0].split('":"')
    #print(token[1])
    # here under lets save the token into a text file
    fa = open("ctr_token.txt", "w")
    fa.write(token[1])
    fa.close()
    return (token[1])  
  

#  def_ask_for_a_token***
def ask_for_a_token():
    '''
    MODIFIED : 2025-07-29

    description : asking for a token to XDR
    
    how to call it : ask_for_a_token() OR access_token=ask_for_a_token()
    '''
    route="/ask_for_a_token"
    env.level+='-'
    print()
    print('\n'+env.level,white('def ask_for_a_token() in functions_for_xdr_asking_for_a_token.py : >',bold=True))
    global client_id
    global client_password
    global host
    global host_for_token
    global profil_name
    print(yellow('STEP 1 - Read Config.txt',bold=True))
    with open('config.txt','r') as file:
        text_content=file.read()
    print(yellow('STEP 2 - Ask for a CTR TOKEN',bold=True))
    client_id,client_password,host_for_token,host,conure = parse_config(text_content) # parse config.txt file
    access_token=get_ctr_token(host_for_token,client_id,client_password)
    print(green('\n'+access_token,bold=True))
    return access_token
    

