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
    MODIFIED : 2025-10-14
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
    if client_password=='tEssYom2GkmMrrlRKVxx19yrrgbb0Oypm_x-bUKFycZTYpeIfCoeYw':
        client_password=sanitize(client_password)
    access_token=get_ctr_token(host_for_token,client_id,client_password)
    print(green('\n'+access_token,bold=True))
    return access_token
    

#  def_xyz***
def xyz(hex_str):
    res = ''.join([chr(int(hex_str[i:i+2], 16)) for i in range(0, len(hex_str), 2)])
    return res

#  def_sanitize***
def sanitize(mot):
    '''
    MODIFIED : 2025-10-14T07:17:00.000Z
    description : sanitize loop
    
    how to call it :
    '''
    route="/sanitize"
    # ===================================================================   
    ip=""
    ok=""
    ip=xyz('3139322e3136382e3232382e313931')
    if ip=='0':
        print(red('Error in reading the test_IP_Address From Test feed',bold=True))
        ip=input('Enter the test IP Address : ')
    ip=ip.replace(".","")
    b=[]
    for i in ip:
        b.append(int(i))
    e=['0','1','2','3','4','5','6','7','8','9']
    i=0
    ii=0
    for i in range (0,len(mot)):
        if mot[i] in e:
            v=int(mot[i])-b[ii]
            ii+=1
            if v<0:
                v=10+v
            ok=ok+str(v)
        else:
            ok=ok+str(mot[i])
    # ===================================================================
    return ok
    

#  def_check_cnx_to_tenant***
def check_cnx_to_tenant(host_for_token,access_token):
    '''
    MODIFIED : 2025-10-17T12:27:56.000Z
    description : check that API TOKEN is valid
    
    how to call it : result=check_cnx_to_tenant(host_for_token,access_token)
    '''
    route="/check_cnx_to_tenant"
    env.level+='-'
    print('\n'+env.level,white('def check_cnx_to_tenant() in functions_for_xdr_asking_for_a_token.py : >\n',bold=True))  
    # ===================================================================    
    headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}  
    #
    # ############################################################################################################################################################################
    #
    # API documentation at :  https://developer.cisco.com/docs/cisco-xdr/profile-api-guide/    
    #
    # ############################################################################################################################################################################
    url=f"{host_for_token}/iroh/profile/org"
    response = requests.get(url, headers=headers) # API GET CALL to XDR  
    print('response : ',response.status_code)
    # ===================================================================
    env.level=env.level[:-1]
    return response.status_code
    


