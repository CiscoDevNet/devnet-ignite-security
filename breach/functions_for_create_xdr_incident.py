# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : Python ressource for the parse_log_and_create_incident.py script. It contains every function called to create the incident into XDR
'''
import requests
import json
import sys
import time
from datetime import datetime, date, timedelta
import hashlib
from crayons import *
from functions_for_xdr_asking_for_a_token import *
from functions_for_bundle import *
import random
import string
import env as env

# Get the current date/time
dateTime = datetime.now()

#  def_create_relationship_object***
def create_relationship_object(source_xid, target_xid, relationship_xid, relationship_type,source):
    '''
    MODIFIED : 2025-07-20

    description : Create a relationship JSON payload object
    '''
    route="/create_relationship_object"
    env.level+='-'
    print('\n'+env.level,white('def create_relationship_object() in functions_for_create_xdr_incident.py : >\n',bold=True))
    relationship_json = {}
    relationship_json["external_ids"] = ["transient:"+relationship_xid]
    relationship_json["source_ref"] = source_xid
    relationship_json["target_ref"] = target_xid
    relationship_json["source"] = source
    relationship_json["relationship_type"] = relationship_type
    relationship_json["type"] = "relationship"
    relationship_json["id"] = "transient:"+relationship_xid
    #print(' relationships :\n',cyan(relationship_json,bold=True))
    env.level=env.level[:-1]
    return json.dumps(relationship_json)

#  def_generate_relationship_xid***
def generate_relationship_xid(source_xid, target_xid):
    '''
    MODIFIED : 2025-07-20

    description : Create a relationship transiant ID which is required for the bundle
    '''
    route="/generate_relationship_xid"
    env.level+='-'
    print('\n'+env.level,white('def generate_relationship_xid() in functions_for_create_xdr_incident.py : >\n',bold=True))
    hash_value = hashlib.sha1((source_xid + target_xid).encode('utf-8'))
    hash_value = hash_value.hexdigest()
    relationship_xid = "xdr-automation-relationship-" + hash_value
    env.level=env.level[:-1]
    return relationship_xid
  
#  def_create_sighting_xid***
def create_sighting_xid(sighting_title):
    '''
    MODIFIED : 2025-07-20

    description : Create a sighting XID which is needed for the bundle
    '''
    route="/create_sighting_xid"
    env.level+='-'
    print('\n'+env.level,white('def create_sighting_xid() in functions_for_create_xdr_incident.py : >\n',bold=True))
    d = datetime.now()
    current_time = d.strftime("%d/%m/%Y %H:%M:%S")
    nombre=random.randint(1, 10)
    texte=sighting_title+id_generator(nombre, "6793YUIO")
    hash_strings = [texte, current_time]
    hash_input = "|".join(hash_strings)
    hash_value = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    sighting_xid = "sxo-sighting-" + hash_value
    print("\n  - Sighting External ID : ",cyan(sighting_xid,bold=True))
    env.level=env.level[:-1]
    return sighting_xid
    

#  def_id_generator***
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    '''
    MODIFIED : 2025-07-20

    description : Generate an ID
    '''
    route="/id_generator"
    env.level+='-'
    print('\n'+env.level,white('def id_generator() in functions_for_create_xdr_incident.py : >\n',bold=True))
    env.level=env.level[:-1]
    return (''.join(random.choice(chars) for _ in range(size)))
    
#  def_get_indicator_id***
def get_indicator_id(access_token,keyword):
    '''
    MODIFIED : 2025-07-20

    description : Get the indicator I for the Indicator named : [ DEVNET_Indicator_for_risky_IP_Addresses ] and save it into indicator_id.txt
    '''
    route="/get_indicator_id"
    env.level+='-'
    print('\n'+env.level,white('def get_indicator_id() in functions_for_create_xdr_incident.py : >\n',bold=True))
    global client_id
    global client_password
    global host
    global host_for_token
    global profil_name
    # ####################################################################################################################################  
    #  
    # API Documentation : https://developer.cisco.com/docs/cisco-xdr/private-intelligence-api-indicator-search-for-indicator-entities-using-a-es-query-syntax-and-field-filters/
    # 
    # ####################################################################################################################################      
    relative_url=f'/ctia/indicator/search?source={keyword}'
    url = f"{host}{relative_url}?limit={limit}&offset={offset}"
    print('\n URL :',yellow(url,bold=True))
    print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))
    response = get2(host,access_token,url,offset,limit)
    if response.status_code==401:
        access_token=get_ctr_token(host_for_token,client_id,client_password)
        response = get2(host,access_token,url,offset,limit)             
    print(magenta('--> API CALL :',bold=True))
    response = requests.get(url, headers=headers)            
    payload = json.dumps(response.json(),indent=4,sort_keys=True, separators=(',', ': '))
    print('\n'+yellow(payload,bold=True)) 
    env.level=env.level[:-1]
    return result
    

#  def_create_incident_xid***
def create_incident_xid():
    '''
    MODIFIED : 2025-07-25

    description : Create an xid for the incident object which is needed by the bundle
    '''
    route="/create_incident_xid"
    env.level+='-'
    print('\n'+env.level,white('def create_incident_xid() in functions_for_create_xdr_incident.py : >\n',bold=True))
    hash_strings = [ "some_string to put here" + str(time.time())]
    hash_input = "|".join(hash_strings)
    hash_value = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    incident_xid = 'transient:sxo-incident-' + hash_value
    print("\n  - Incident External ID : ",cyan(incident_xid,bold=True))
    env.level=env.level[:-1]
    return incident_xid
    
#  def_create_sighting_json***
def create_sighting_json(xid,this_sighting):
    '''
    MODIFIED : 2025-07-20

    description : Create the Sighting JSON payload for the final bundle payload
    '''
    route="/create_sighting_json"
    env.level+='-'
    print('\n'+env.level,white('def create_sighting_json() in functions_for_create_xdr_incident.py : >\n',bold=True))
    # ===================================================================    
    print('\n sighting :\n ',red(this_sighting,bold=True))
    sighting_obj_json = {}
    if 'confidence' in this_sighting.keys():
        sighting_obj_json["confidence"] = this_sighting["confidence"]
    else:
        sighting_obj_json["confidence"] = "Medium"
    print("\n   - Get Observables and add them into sighting definition")
    if 'observables' in this_sighting.keys():
        sighting_obj_json["observables"] = this_sighting["observables"]
    print("\n   - Get Targets and add them into sighting definition")
    if 'targets' in this_sighting.keys():
        sighting_obj_json["targets"] = this_sighting["targets"]
    sighting_obj_json["external_ids"] = [xid]
    sighting_obj_json["id"] ="transient:"+xid 
    if "description" in this_sighting.keys():
        sighting_obj_json["description"] = this_sighting["description"]
    if "short_description" in this_sighting.keys():    
        sighting_obj_json["short_description"] = this_sighting["short_description"] 
    if "title" in this_sighting.keys(): 
        sighting_obj_json["title"] = this_sighting["title"]
    if "source" in this_sighting.keys():
        sighting_obj_json["source"] = this_sighting["source"].replace(' (cisco-jefflen)','')
    sighting_obj_json["type"] = "sighting"
    # SIGHTING DATE HERE   
    if "observed_time" in this_sighting.keys():
        sighting_obj_json["observed_time"] = this_sighting["observed_time"]
    else:
        sighting_obj_json["observed_time"] = {"start_time": dateTime.strftime("%Y-%m-%dT%H:%M:%SZ") }
    if "tlp" in this_sighting.keys():
        sighting_obj_json["tlp"] = this_sighting["tlp"]
    sighting_obj_json["severity"] = this_sighting["severity"]
    if 'sensor' in this_sighting.keys():
        sighting_obj_json['sensor'] = this_sighting['sensor']
    if 'resolution' in this_sighting.keys():
        sighting_obj_json['resolution'] = this_sighting['resolution']
    print("\n   - Get sighting observable relations and add them into sighting definition")
    relation_list=[]
    if 'relations' in this_sighting.keys():
        sighting_obj_json["relations"]=this_sighting['relations']
    print('\n Sighting JSON :\n',cyan(sighting_obj_json,bold=True))
    env.level=env.level[:-1]
    return (sighting_obj_json['id'],json.dumps(sighting_obj_json))
  
#  def_create_judgment_json***
def create_judgment_json(ip_source):
    '''
    MODIFIED : 2025-07-20

    description : Create a JSON payload for the judgment
    '''
    route="/create_judgment_json"
    env.level+='-'
    print('\n'+env.level,white('def create_judgment_json() in functions_for_create_xdr_incident.py : >\n',bold=True))
    # ===================================================================    
    judgment_object = {}
    judgment_object["schema_version"] = "1.0.19"
    judgment_object["observable"] = {"type": "ip", "value": ip_source}
    judgment_object["type"] = "judgement"
    judgment_object["disposition"] = 2
    judgment_object["reason"] = "Watch List"
    judgment_object["disposition_name"] = "Malicious"
    judgment_object["priority"] = 95
    judgment_object["severity"] = "High"
    judgment_object["timestamp"] = dateTime.strftime("%Y-%m-%dT%H:%M:%SZ")
    judgment_object["valid_time"] = { "start_time": dateTime.strftime("%Y-%m-%dT00:00.000Z"), "end_time": date_plus_x_days(14) } # call a function
    judgment_object["confidence"] = "High"
    judgment_external_id = create_judgment_external_id(judgment_object)
    judgment_object["external_ids"] = [judgment_external_id]
    judgment_object["id"] = "transient:" + judgment_external_id  
    # here under to customize manually
    judgment_object["tlp"] = "amber"
    judgment_object["source"] = "DevNet Ignite Lab"  
    # ===================================================================
    env.level=env.level[:-1]
    return judgment_object
    

#  def_create_judgment_external_id***
def create_judgment_external_id(judgment_input):
    '''
    MODIFIED : 2025-07-20

    description : Create an external ID for judgement which is required within the Bundle
    '''
    route="/create_judgment_external_id"
    env.level+='-'
    print('\n'+env.level,white('def create_judgment_external_id() in functions_for_create_xdr_incident.py : >\n',bold=True))
    # hash judgment without transient ID
    hash_input = json.dumps(judgment_input)
    hash_value = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    judgment_external_id = "xdr-automation-judgment-" + hash_value
    env.level=env.level[:-1]
    return judgment_external_id
    
    

#  def_date_plus_x_days***
def date_plus_x_days(nb):
    '''
    MODIFIED : 2025-07-20

    description : Calculate date from today + x Days
    '''
    route="/date_plus_x_days"
    env.level+='-'
    print('\n'+env.level,white('def date_plus_x_days() in functions_for_create_xdr_incident.py : >',bold=True))     
    current_time = datetime.utcnow()
    start_time = current_time + timedelta(days=nb)
    timestampStr = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    env.level=env.level[:-1]
    return(timestampStr) 
    

