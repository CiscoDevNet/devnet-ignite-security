# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : read the ip_addresses.txt file and add every ip addresses it contains into it. Creat judgent for every ip addresses as malicious
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


#  def_inspect_the_text***
def inspect_the_text(host,access_token,text):
    '''
    MODIFIED : 2025-07-30

    description : query XDR inspect API in order to create the observable list value and type
    '''
    env.level+='-'
    print('\n'+env.level,white('def inspect_the_text() in add_ip_addresses_into_feeds.py : >\n',bold=True))

    print('Text to inspect :\n',cyan(text,bold=True))
    url = f'{host}/iroh/iroh-inspect/inspect'
    headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}

    inspect_payload = {"content":text}
    inspect_payload = json.dumps(inspect_payload)  
    print(magenta('\n--> API CALL : to the XDR Inspect API',bold=True))
    try:
        response = requests.post(url, headers=headers, data=inspect_payload)
        print('\nstatus code :',yellow(response.status_code,bold=True))
        print()          
        if response.status_code==200:
            print(green("\nHTTP CALL SUCCESFUL",bold=True)) 
            print('\nresponse :\n',green(response.json()))            
        elif response.status_code==401:
            print(yellow("NEED TO RENEW THE TOKEN\n",bold=True)) 
            client_id,client_password,host_for_token,host,conure = parse_config(text_content) # parse config.txt file
            access_token=get_ctr_token(host_for_token,client_id,client_password)
            print(magenta('\n--> NEW API CALL with a new token : to the XDR Inspect API',bold=True))
            headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
            response = requests.post(url, headers=headers, data=inspect_payload)
            print('\nstatus code :',yellow(response.status_code,bold=True))
        print('\nresponse : ',response.json())
    except:
        print(red("\nHTTP GET FAILED DURING XDR INSPECT CALL\n",bold=True))
        print()    
        sys.exit()   
    observables=json.dumps(response.json(),sort_keys=True,indent=4, separators=(',', ': '))
    print('\nobservables:\n',cyan(observables,bold=True))      
    env.level=env.level[:-1]
    return(observables,response.status_code)
    
#  def_create_judgments_json_payload_and_attach_to_feed***
def create_judgments_and_attach_to_feed(data,indicator_id,host):
    '''
    MODIFIED : 2025-07-30

    description : Create one or several judgment located into data, into XDR. And link them to an indicator in order to add them into the feed attached to the indicator
    '''
    route="/create_judgments_and_attach_to_feed"
    env.level+='-'
    print('\n'+env.level,white('def create_judgments_and_attach_to_feed() in add_ip_addresses_into_feeds.py : >\n',bold=True))
    print(cyan(f"- indicator_id : {indicator_id}\n",bold=True))
    with open('ctr_token.txt','r') as file0:
        access_token=file0.read()
    nb=0
    judgments_new=[]
    for item in data:
        print(yellow(f"\n- item : {item}\n",bold=True))     
        if nb<1000:
              # here under create the judgment JSON payload
            judgment_object = {}
            judgment_object["schema_version"] = "1.0.19"
            judgment_object["observable"] = item["observable"]
            judgment_object["type"] = "judgement"
            judgment_object["disposition"] = item["disposition"]
            judgment_object["reason"] = "Watch List"
            judgment_object["disposition_name"] = item["disposition_name"]
            judgment_object["priority"] = item["priority"]
            judgment_object["severity"] = item["severity"]
            judgment_object["timestamp"] = dateTime.strftime("%Y-%m-%dT%H:%M:%SZ")
            judgment_object["valid_time"] = item["valid_time"]
            judgment_object["confidence"] = item["confidence"]
            judgment_external_id = create_judgment_external_id(judgment_object) # call a function
            judgment_object["external_ids"] = [judgment_external_id]
            judgment_object["id"] = "transient:" + judgment_external_id  
            # here under to customize manually
            judgment_object["tlp"] = item["tlp"]
            judgment_object["source"] = item["source"]           
            judgments_new.append(judgment_object)
            nb+=1
        else:
              # we go to this branch because we have more than 1000 judgments. 
            judgment_transient_ids = [judgement["id"] for judgement in judgments_new] # create a transient ID for judgment
            relationships_new = [] # create the new relatioship list
            for judgment_id in judgment_transient_ids:
                relationship_object = {}
                relationship_xid=generate_relationship_xid(judgment_id,indicator_id)  # create a transient ID for relationship
                create_relationship_json_payload(relationship_object,judgment_id,indicator_id,relationship_xid)  # create a relationship for judgment to indicator
                relationships_new.append(relationship_object) # add new relatioship to relationship list
            # here under lets create the Bundle JSON Payload
            bundle_object = {} 
            source="DevNet Ignite Lab"
            incidents=[]
            sightings=[]
            indicators=[]
            #judgments_new=[]
            #relationships_new=[]
            create_bundle_json(source,incidents,sightings,indicators,judgments_new, relationships_new) # create the JSON payload
            bundle_object = json.dumps(bundle_object)
            post_bundle(bundle_object,access_token,host) # call a function post this bundle with 100 entries            
            judgments_new.clear()
            nb=0
    judgment_transient_ids = [judgement["id"] for judgement in judgments_new] # create a transient ID for judgment
    relationships_new = [] # create the new relatioship list
    for judgment_id in judgment_transient_ids:
        relationship_object = {}
        relationship_xid=generate_relationship_xid(judgment_id,indicator_id)  # create a transient ID for relationship
        create_relationship_json_payload(relationship_object,judgment_id,indicator_id,relationship_xid)  # create a relationship for judgment to indicator
        relationships_new.append(relationship_object) # add new relatioship to relationship list
    # here under create the Bundle JSON payload
    source="DevNet Ignite Lab"
    incidents=[]
    sightings=[]
    indicators=[]
    #judgments_new=[]
    #relationships_new=[]
    bundle_object = {}
    bundle_object = create_bundle_json(source,incidents,sightings,indicators,judgments_new, relationships_new)    # create the JSON paylaod
    bundle_object = json.dumps(bundle_object)
    print('\nbundle_object :',cyan(bundle_object,bold=True))
    a = input('Bundle JSON Payload above ready to be posted ( type ENTER to continue ) : ')
    post_bundle(bundle_object,access_token,host) # post the bundle
    env.level=env.level[:-1]
    return 1

#  def_create_judgments_json_payload***
def create_judgments_json_payload(observables,disposition_name,priority,severity,confidence,tlp,type,source):
    '''
    MODIFIED : 2025-07-29

    description : Create a judgments JSON data from the observables list given as an input
    '''
    route="/create_judgments_json_payload"
    env.level+='-'
    print('\n'+env.level,white('def create_judgments_json_payload() in add_ip_addresses_into_feeds.py : \n>',bold=True))
    observables=json.loads(observables)       
    copied_judgements={}        
    copied_judgements['data']=[]
    if disposition_name=='Clean':
        disposition=1
    elif disposition_name=='Malicious':
        disposition=2
    else:
        disposition=3       
    with open('./judgments_json_payload.json','w') as file: # saved resulting file chunk
        for item in observables:
            obs={}
            for k,v in item.items():
                obs[k]=v
            temp_dict={}
            temp_dict['observable']=obs
            temp_dict['disposition']=disposition
            temp_dict['disposition_name']=disposition_name
            temp_dict['priority']=int(priority)
            temp_dict['severity']=severity
            temp_dict['confidence']=confidence
            temp_dict['tlp']=tlp
            temp_dict['source']=source
            temp_dict['valid_time']={ "start_time": dateTime.strftime("%Y-%m-%dT00:00.000Z"), "end_time": date_plus_x_days(14) } # call a function
            if temp_dict['observable']['type']==type:
                copied_judgements['data'].append(temp_dict)
                print(cyan(f"`n- temp_dict : {temp_dict}\n",bold=True))
        print(yellow(f"\n- copied_judgements : {copied_judgements}\n",bold=True))
        file.write(json.dumps(copied_judgements,sort_keys=True,indent=4, separators=(',', ': '))) # convert JSON result into readable formt and saved it into resulting file
    env.level=env.level[:-1]
    return 1  
  
#  def_date_plus_x_days***
def date_plus_x_days(nb):
    '''
    MODIFIED : 2025-07-20

    description : current time + nb days in the YYYY-mm-ddTH:M:S.fZ format
    '''
    route="/date_plus_x_days"
    env.level+='-'
    print('\n'+env.level,white('def date_plus_x_days() in add_ip_addresses_into_feeds.py : >\n',bold=True))
    current_time = datetime.utcnow()
    start_time = current_time + timedelta(days=nb)
    timestampStr = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    env.level=env.level[:-1]
    return(timestampStr) 

if __name__=="__main__":
    '''
        modidfied : 2025-09-10
    '''
    print(cyan('-> Let\'s get API credentials',bold=True))
    print()    
    with open('config.txt','r') as file:
        text_content=file.read()
    client_id,client_password,host_for_token,host,conure = parse_config(text_content)
    fa = open("ctr_token.txt", "r")
    access_token = fa.readline()
    fa.close()
    print(cyan('-> First let\'s read the ip_addresses.txt file ',bold=True))    
    with open('ip_addresses.txt') as file:
        text_content=file.read()
    print(cyan('\n--> second let\'s convert the file content into an observable list ',bold=True))
    print(magenta('\n--> CALL FUNCTION : inspect_the_text',bold=True))
    observable_list,status_code=inspect_the_text(host_for_token,access_token,text_content) # parse raw text content and extract observables and their types
    print('\nobservable list :\n',yellow(observable_list,bold=True))  
    with open('./indicator_id.txt') as file:
        indicator_id=file.read()
    print(magenta('\n--> CALL FUNCTION : create_judgments_json_payload',bold=True))        
    disposition_name="Malicious"
    severity="High"
    priority=95
    confidence="High"
    tlp="green"
    type="ip"
    source="DevNet Ignit Lab"
    create_judgments_json_payload(observable_list,disposition_name,priority,severity,confidence,tlp,type,source) # create judgment JSON payload
    with open('./judgments_json_payload.json') as file:
        json_payload=file.read()
    data=json.loads(json_payload)['data']  
    text_result=json.dumps(data,sort_keys=True,indent=4, separators=(',', ': '))    
    print('\ntext_result :',cyan(text_result,bold=True)) 
    create_judgments_and_attach_to_feed(data,indicator_id,host) # call function that POST judgments in destination XDR tenant
    print(green('\nOK DONE. You can check Feed content in XDR',bold=True))
 

