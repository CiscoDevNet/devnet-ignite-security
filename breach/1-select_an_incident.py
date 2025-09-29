# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : Get incident list and select an incident in the list
'''
import requests
import json
from crayons import *
import os
import sys
from functions_for_xdr_asking_for_a_token import *

item_list=[]
source_to_select="ALL"

#  def_get***
def get(host,access_token,url,offset,limit):
    '''
    MODIFIED : 2025-07-25T12:01:00.000Z

    description : generic and very basic http get function for XDR
    
    how to call it : response = get(host,access_token,url,offset,limit)
    '''
    route="/get"
    env.level+='-'
    print('\n'+env.level,white('def get() in 1-select_an_incident.py : >\n',bold=True))
    headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
    url = f"{host}{url}?limit={limit}&offset={offset}"
    response = requests.get(url, headers=headers)    # API CALL HERE
    return response
    
#  def_get_incidents***
def get_incidents(host,access_token,client_id,client_password,host_for_token):
    '''
    MODIFIED : 2025-07-25T12:06:36.000Z
    description : Get incidents in XDR tenant with legacy APIs ( not CONURE )
    
    how to call it :
    '''
    route="/get_incidents"
    env.level+='-'
    print('\n'+env.level,white('def get_incidents() in 1-select_an_incident.py : >\n',bold=True))
    url = "/ctia/incident/search"
    offset=0
    limit=1000
    go=1 # used to stop the loop   
    while go:      
        index=0
        print(magenta('\nSend API to XDR tenant and get incident list :',bold=True))
        response = get(host,access_token,url,offset,limit)
        print(response)
        if response.status_code==401:
            print(magenta('\n2nd try with new token - Send API to XDR tenant and get incident list :',bold=True))
            access_token=get_ctr_token(host_for_token,client_id,client_password)
            response = get(host,access_token,url,offset,limit)
        payload = json.dumps(response.json(),indent=4,sort_keys=True, separators=(',', ': '))
        #print(response.json())
        print(yellow('\nIncidents into the XDR Tenant :\n',bold=True))
        items=response.json()
        if items:
            for item in items:
                #print(yellow(item,bold=True))
                if item['id'] not in item_list:
                    item_list.append(item['id'])
                print(str(index),' : ',item['title'])
                index+=1
        else:
            print(red('\nThere is no Incident yet in this tenant !',bold=True))
            print(white('No Problem you must try again when you have Incidents',bold=True))
            sys.exit()
        if index>=limit-1:
            go=1
            offset+=index-1
        else:
            go=0
    i=0
    print()
    a=input(yellow('\nWhich Incident do you want to select ? ( enter incident index ) : ',bold=True))
    if a:
        index=int(a)
    else:
        print(red('\nError ! : You must Select an Incident !',bold=True))
        sys.exit()
    return (item_list[index])

#  def_main***
def main():
    '''
    MODIFIED : 2025-09-10
    description : main function 
    
    how to call it : main()
    '''
    route="/main"
    env.level+='-'
    print('\n'+env.level,white('def main() in 1-select_an_incident.py : >\n',bold=True))
    with open('config.txt','r') as file:
        text_content=file.read()
    #host = parse_config(text_content)
    client_id,client_password,host_for_token,host,conure = parse_config(text_content)
    fa = open("ctr_token.txt", "r")
    access_token = fa.readline()
    fa.close()
    print(yellow('\n- Get Incidents first',bold=True))
    incident_ID=get_incidents(host,access_token,client_id,client_password,host_for_token)
    incident_ID=incident_ID.replace(host+':443/ctia/incident/','')
    print("\nSelected Incident ID is : \n",cyan(incident_ID,bold=True))
    with open('./incident_id.txt','w') as file:
        file.write(incident_ID)
    return 1
  

if __name__=="__main__":
    print("start here")
    main()
    print(green("OK DONE",bold=True))
