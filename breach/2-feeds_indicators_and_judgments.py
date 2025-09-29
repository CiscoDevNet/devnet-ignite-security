# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : Create feed and attach it to an Indicator that is created as well. And Add a list of observables into this feed
'''
import requests
import json
import sys
from datetime import datetime, date, timedelta
import hashlib
from crayons import *
from functions_for_xdr_asking_for_a_token import *
from functions_for_bundle import *
from functions_for_feeds_indicators_and_judgments import *
import env as env

# Get the current date/time
dateTime = datetime.now()

#  def_create_indicator***
def create_indicator(host,access_token,indicator_name,indicator_type,description,source,create_in_xdr):
    '''
    MODIFIED : 2025-07-20

    description : Create an Indicator into XDR
    '''
    route="/create_indicator"
    env.level+='-'
    print('\n'+env.level,white('def create_indicator() in feeds_indicators_and_judgments.py : >\n',bold=True))
    global client_id
    global client_password
    if indicator_type=="IPv4":
        indic_type=["IP Watchlist"]
    elif indicator_type=="IPv6":
        indic_type=["IP Watchlist"]  
    elif indicator_type=="DOMAIN":
        indic_type=["Domain Watchlist"] 
    elif indicator_type=="URL":
        indic_type=["URL Watchlist"]  
    elif indicator_type=="SHA256":
        indic_type= ["File Hash Watchlist"]
    else:
        indic_type=[]
        indic_type.append(indicator_type)
    # Get the current date/time
    dateTime = datetime.now()
    # Build the indicator JSON Payload
    indicator_object = {}
    indicator_object["description"] = description
    indicator_object["producer"] = "DevNet Ignite Lab"
    indicator_object["schema_version"] = "1.0.19"
    indicator_object["type"] = "indicator"
    indicator_object["source"] = source
    indicator_object["short_description"] = description
    indicator_object["title"] = indicator_name
    indicator_object["indicator_type"] = indic_type
    indicator_object["severity"] = "Info"
    indicator_object["tlp"] = "amber"
    indicator_object["timestamp"] = dateTime.strftime("%Y-%m-%dT00:00.000Z")
    indicator_object["confidence"] = "High" 
    # convert dict to json
    #payload = json.dumps(indicator_object)  
    payload = json.dumps(indicator_object,indent=4,sort_keys=True, separators=(',', ': '))     
    print('\n indicator JSON : \n',cyan(payload,bold=True))       
    create_in_xdr='YES' # for futur use
    indicator_id='none'
    if create_in_xdr=='YES':
        #POST / Create Indicator into XDR
        # #########################################################################################################################
        #
        # API documentation : https://developer.cisco.com/docs/cisco-xdr/private-intelligence-api-indicator-adds-a-new-indicator/
        #
        # #########################################################################################################################         
        url = f'{host}/ctia/indicator'
        print('\nurl :',yellow(url,bold=True))
        headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
        print(magenta('\n--> API CALL :',bold=True))
        response = requests.post(url, headers=headers, data=payload)
        print('response status code :\n',cyan(response.status_code,bold=True))
        print('\nresponse :\n',cyan(response.content,bold=True))
        if response.status_code==401:
            access_token=get_ctr_token(host_for_token,client_id,client_password)
            headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
            response = requests.post(url, headers=headers, data=payload)
        print(green(response.json(),bold=True))  
        indicator_id=response.json()['id']
    return(indicator_id,response.status_code)
#  def_create_feed***
def create_feed(host,access_token,indicator_id,feed_name):
    '''
    MODIFIED : 2025-09-02
    description : Create a feed into XDR
    '''
    route="/create_feed"
    env.level+='-'
    print('\n'+env.level,white('def create_feed() in feeds_indicators_and_judgments.py : >\n',bold=True))
    global client_id
    global client_password
    # Get the current date/time
    dateTime = datetime.now()
    # Build the feed JSON payload
    feed_object = {}
    feed_object["schema_version"] = "1.0.19"
    feed_object["indicator_id"] = indicator_id
    feed_object["type"] = "feed"
    feed_object["output"] = "observables"
    feed_object["title"] = feed_name
    feed_object["tlp"] = "amber"
    feed_object["lifetime"] = {
        "start_time": dateTime.strftime("%Y-%m-%dT00:00.000Z")
    }
    feed_object["timestamp"] = dateTime.strftime("%Y-%m-%dT00:00.000Z")
    feed_object["feed_type"] = "indicator"
    payload = json.dumps(feed_object)
    print()
    print(' feed JSON : \n',cyan(payload,bold=True))
    #POST / Create Indicator into XDR
    # ############################################################################################################
    #
    # api documentation https://developer.cisco.com/docs/cisco-xdr/private-intelligence-api-feed-adds-a-new-feed/
    #
    # ############################################################################################################    
    url = f'{host}/ctia/feed'
    headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
    print(magenta('\n--> API CALL THAT CREATE THE FEED :\n',bold=True))
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code==401:
        access_token=get_ctr_token(host_for_token,client_id,client_password)
        headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
        response = requests.post(url, headers=headers, data=payload) # API POST CALL
    print (yellow(response,bold=True))  
    print(green(response.json(),bold=True))  
    feed_id=response.json()['id']
    feed_url=response.json()['feed_view_url']
    print('\n result : ',green(response.json(),bold=True))     
    env.level=env.level[:-1]
    return(feed_id,feed_url,response.status_code)
    

if __name__=="__main__":
    print()
    print(cyan('Let\' recap what we aregoing to do',bold=True))    
    print()
    print(cyan('-> First we will read the config.txt file and parse connexion details',bold=True))
    print(cyan('-> Then we will ask for an API token to XDR',bold=True))    
    print(cyan('-> Then we will create the Indicator',bold=True))
    print(cyan(' -> Then we will create the feed and attach it to the Indicator we created prior',bold=True))    
    print(cyan('  -> Then we will read the ip_addresses.txt file and extract every single ip addresses into a python list',bold=True))   
    print(cyan('   -> For each ip address in the list, we will add it into a judgment JSON payload',bold=True))
    print(cyan('   -> We will link this judgment to the Indicator',bold=True))    
    print(cyan('    -> Then we will create a bundle with only judgments and relationship payloads into it',bold=True))    
    print(cyan('     -> Finally we will post the bundle into XDR',bold=True)) 
    print(cyan('      -> DONE',bold=True))     
    print()
    a = input('let\'s go for it ( type any key ) ? :') 
    print(cyan('-> Let\s get API credentials\n',bold=True)) 
    with open('config.txt','r') as file:
        text_content=file.read()
    client_id,client_password,host_for_token,host,conure = parse_config(text_content) # parse config.txt
    access_token=get_ctr_token(host_for_token,client_id,client_password)
    '''
    fa = open("ctr_token.txt", "r")
    access_token = fa.readline()
    fa.close()
    host="https://private.intel.eu.amp.cisco.com"    
    '''
    print(yellow('-> First let\'s create the Indicator',bold=True)) 
    indicator_name=input(yellow('\nEnter Indicator Name ( default : DevNet_Indicator_for_risky_IP_Addresses ): ',bold=True))
    indicator_name=indicator_name.strip()
    if indicator_name=='':
        indicator_name='DEVNET_Indicator_for_risky_IP_Addresses'
    print(magenta(f'\n--> CALL  A SUB FUNCTION : create the indicator {indicator_name}',bold=True))    
    indicator_type='IPv4'
    description='Example of Indicator for risky IP Addresses'
    source='DevNet Ignite Lab'
    create_in_xdr='YES'
    indicator_id,status_code=create_indicator(host,access_token,indicator_name,indicator_type,description,source,create_in_xdr)
    print('\nstatus code : ',yellow(status_code,bold=True))           
    if status_code==201:
        print(green("\nHTTP REST CALL SUCCEEDED",bold=True))
    else:
        print(red("\nHTTP REST CALL FAILED line #45",bold=True))
        sys.exit()
    print('\n indicator_id : ',green(indicator_id,bold=True))
    with open('indicator_id.txt','w') as file:
        file.write(indicator_id)
    a = input(white('\nOK Press Enter for Next Step...',bold=True)) 
    print(cyan('\n--> Now let\'s create the Feed',bold=True))
    feed_name=input(yellow('\nEnter a Feed Name ( default : DevNet_Feed_for_risky_IP_Addresses ): ',bold=True))
    feed_name=feed_name.strip()
    if feed_name=='':
        feed_name='DevNet_Feed_for_risky_IP_Addresses'
    print(magenta(f'\n--> CALL  A SUB FUNCTION : create the feed : {feed_name}',bold=True))
    feed_id,feed_url,status_code=create_feed(host,access_token,indicator_id,feed_name)
    print('\nstatus code : ',yellow(status_code,bold=True))           
    if status_code==201:
        print(green("\nHTTP REST CALL SUCCEEDED",bold=True))
        print('feed URL :\n',green("\n"+feed_url,bold=True))
    else:
        print(red("HTTP REST CALL FAILED line #63",bold=True))
        sys.exit()
    print('\nfeed_id : ',green(feed_id,bold=True))
    with open('feed_id.txt','w') as file:
        file.write(feed_id)
    with open('feed_url.txt','w') as file:
        file.write(feed_url)
    print(yellow('\nCopy and save somewhere the Feed URL above. You can open it into your browser',bold=True))        
    print(cyan('\nOK NEXT STEP WILL BE TO ADD IP ADDRESSES INTO FEEDS. Run the 3-add_ip_addresses_into_feeds.py script for this',bold=True))
    

