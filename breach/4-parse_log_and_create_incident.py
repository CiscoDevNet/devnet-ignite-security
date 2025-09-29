# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : parse the syslog,  extract relevant object needed for the Incident and Call create Incident creation functions
'''
import requests
import json
import sys
from datetime import datetime, date, timedelta
from crayons import *
import env as env
from functions_for_xdr_asking_for_a_token import *
from functions_for_bundle import *
from functions_for_create_xdr_incident import *

incidents={}
incidents_counts={}
indicator_list=[] 
save_sightings=0 # save every sightings as separate file into ./sightings for futur corellation
client_id=''
client_password=''
host_for_token=''
host=''

#  def_parse_syslog***
def parse_syslog(syslog_message):
    '''
    MODIFIED : 2025-07-20

    description : parse syslog message and extract objects needed for the XDR Sighting
    '''
    route="/parse_syslog"
    env.level+='-'
    print('\n'+env.level,white('def parse_syslog() in parse_log_and_create_incident.py : >',bold=True))
    log={}
    #
    # Parse the syslog message :
    #
    fields=syslog_message.split(',')
    timestamp=fields[0].split('  :')[0]
    timestamp=timestamp.split('>')[1]            
    DeviceUUID=fields[0].split(': ')[3]
    SrcIP=fields[4].split(': ')[1]
    DstIP=fields[5].split(': ')[1]
    SrcPort=fields[6].split(': ')[1]
    DstPort=fields[7].split(': ')[1]
    Protocol=fields[8].split(': ')[1]
    Priority=fields[13].split(': ')[1]
    Message=fields[17].split(': ')[1]
    Classification=fields[18].split(': ')[1]
    Client=fields[19].split(': ')[1]
    ApplicationProtocol=fields[20].split(': ')[1]
    #
    # here under put the variables from the syslog, that will be used for creating the Sighting JSON Payload :
    #
    log['timestamp']=timestamp
    log['DeviceUUID']=DeviceUUID
    log['SrcIP']=SrcIP
    log['DstIP']=DstIP
    log['SrcPort']=SrcPort
    log['DstPort']=DstPort
    log['Protocol']=Protocol
    log['Priority']=Priority           
    log['Message']=Message            
    log['Classification']=Classification
    log['Client']=Client
    log['ApplicationProtocol']=ApplicationProtocol
    #
    # done => next
    #
    print("===============================================================================================")    
    print(cyan('PARSING RESULT HERE AFTER :',bold=True))
    print(red('< ALERT ! >\n',bold=True), timestamp,' From ',green(SrcIP,bold=True),' to => ',cyan(DstIP,bold=True),'\n',red(Message,bold=True),'\n','Priority = '+Priority)
    #print(yellow(log,bold=True))
    print("===============================================================================================")    
    env.level=env.level[:-1]
    return(log)
  
#  def_create_a_sighting_json***
def create_a_sighting_json(log):
    '''
    MODIFIED : 2025-07-25

    description : create a sighting JSON payload from the objects dict given as an input and return it
    '''
    route="/create_a_sighting_json"
    env.level+='-'
    print('\n'+env.level,white('def create_a_sighting_json() in parse_log_and_create_incident.py : >',bold=True))
    #
    # create the sighting json payload :
    #
    sighting={}
    date_and_time=current_date_time()
    observables=[{"value": log['SrcIP'],"type": "ip"},{"value": log['DstIP'],"type": "ip"}]
    relations=[
    {
      "relation": "Connected_To",
      "origin":"FTD Syslog server",
      "source": {
        "value": log['SrcIP'],
        "type": "ip"
      },
      "related": {
        "value": log['DstIP'],
        "type": "ip"
      }
    }
  ]
    targets= [
    {
      "type": "endpoint",
      "observables": [
        {
          "value": log['DstIP'],
          "type": "ip"
        }
      ],
      "observed_time": {
        "start_time": date_and_time,
        "end_time": date_and_time
      }
    }
  ]
    observed_time = {
    "start_time": date_and_time,
    "end_time": date_and_time
  }
    if log['Priority']=="1":
       sighting['severity']="Critical"
    elif log['Priority']=="2":
       sighting['severity']="High"
    elif log['Priority']=="3":
       sighting['severity']="Medium"    
    else: 
       sighting['severity']="Low"         
    sighting['observables']=observables
    sighting['relations']=relations
    sighting['source']="Custom_Syslog_Server"
    sighting['targets']=targets
    sighting["short_description"]=log['Message']
    sighting["title"]="IPS Alert SrcIP : "+log['SrcIP']+' to DstIP : '+log['DstIP']
    sighting["confidence"]= "High"
    sighting["observed_time"]= observed_time
    sighting["sensor"]= "network.firewall"
    sighting["description"]= "Network IPS Alert : "+log['Classification']+', between SrcIP : '+log['SrcIP']+' SrcPort : '+log['Protocol']+'/'+log['SrcPort']+' To DstIP : '+log['DstIP']+' DstPort : '+log['Protocol']+'/'+log['DstPort']+', Client : '+log['Client']+', Application : '+log['ApplicationProtocol']
    #
    # create the sighting json paylod = Ok Done
    #
    print('\n Here is the sighting Json payload :\n',cyan(sighting,bold=True))
    return sighting
    

#  def_create_an_xdr_incident***
def create_an_xdr_incident(all_sightings,ip_source,incident_title):
    '''
    MODIFIED : 2025-07-25

    description : takes sighting in input and create the XDR Incident
    '''
    route="/create_an_xdr_incident"
    env.level+='-'
    print('\n'+env.level,white('def create_an_xdr_incident() in parse_log_and_create_incident.py : >\n',bold=True))
    print(yellow("\nNEXT : Create the Incident JSON payload => \n",bold=True))   
    a = input('type Enter : ')  
    print(yellow("\n- > Create Incident JSON and incident_xid needed for the bundle\n",bold=True))
    #
    # prepare parameter values for the incident here under ( static value for the demo ) :
    #
    description= "Source IP address had been seen launching Attacks to Destination IP address"
    source= "FTD Syslog server"
    short_description= "Source IP address had been seen launching Attacks to Destination IP address"
    tlp= "amber"
    confidence= "High"
    severity= "High"
    techniques= []
    tactics= ["TA0002", "TA0005", "TA0006", "TA0007", "TA0008"] # arbitrary values just for demo
    asset_score=10     
    ttp_score=90    
    #
    # prepare parameter values for the incident here under ( static value for the demo ) : OK Done
    #
    #
    # => Create the Incident JSON payload and incident_xid needed for the bundle :
    #    
    incident_json,incident_xid=create_incident_json(incident_title,description,source,short_description,tlp,confidence,severity,techniques,tactics,asset_score,ttp_score) # call a function
    incidents=[]
    incidents.append(json.loads(incident_json))        
    print('\nincident_json : ',yellow(incident_json,bold=True))    
    print('\nincident_xid : ',yellow(incident_xid,bold=True))                 
    #
    # = Create the Incident JSON payload and incident_xid needed for the bundle : Ok Done
    #   
    #print(green('OK DONE : Lets Create the JSON Bundle',bold=True))  
    print(yellow('\nNEXT : Create sighting + relationship json payloads from sithging list given as input => \n',bold=True))
    a = input('type Enter : ')
    #
    # => Create sighting + relationship json payloads from sithging list given as input :
    #     
    sightings=[] # for storing the sightings to add into the bundle
    relationships_new=[] # for storing the relationships to add into the bunbdle
    global indicator_list # in order to attach the sighting to the indicator created prior
    # lets attach sightings to the indicator created in lab 2
    with open('./indicator_id.txt') as file:
        indicator_id=file.read()
    indicator_list.append(indicator_id) # add the indicator_id to the indicator_list
    for this_sighting in all_sightings:    # go to every sightings one by one
        print('\n this sighting : \n',cyan(this_sighting,bold=True))         
        print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))   
        sighting_xid = create_sighting_xid("Sighting created for asset enrichment test") # call a function
        sighting_transient_id="transient:"+sighting_xid
        print("\n  - This Sighting_transient_id : ",cyan(sighting_transient_id,bold=True))
        print("\n  - Create This Sighting json payload with : ",cyan(sighting_transient_id,bold=True)) 
        print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))               
        new_sighting_id,sighting=create_sighting_json(sighting_xid,this_sighting) # call a function
        sightings.append(json.loads(sighting)) # adding this sighting to sighting list
        print('\n   -- ok done')                    
        print(yellow("\n- > lets Create Relationship payload for sighting to Indicator relationship",bold=True))               
        print('\nindicator_list :\n',cyan(indicator_list,bold=True))              
        for indicator in indicator_list:
            the_new_indicator_id=indicator.split('***')[0]
            print('\n--- OK lets create the indicator relationship')              
            print('\nnew indicator id :\n',cyan(the_new_indicator_id,bold=True))   
            print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))   
            nombre=random.randint(1, 10)                 
            random_xid=id_generator(nombre, "6793YUIO")     # call a function  
            print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))                     
            relationship_xid=generate_relationship_xid(the_new_indicator_id,random_xid) # call a function
            print('\nrelationship_xid : ',cyan(relationship_xid,bold=True))
            print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))                     
            relationship=create_relationship_object(sighting_transient_id,the_new_indicator_id,relationship_xid,"sighting-of","XDR Side Car")   # call a function
            relationships_new.append(json.loads(relationship)) # adding this relationship to  relationship list    
        print(yellow("\n- > Create Relationship payload for sighting to Incident memberships. Sighting is member-of Incident",bold=True))
        print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))      
        nombre=random.randint(1, 10)                         
        random_xid=id_generator(nombre, "6723YUIO") 
        relationship_xid=generate_relationship_xid(sighting_transient_id,random_xid) # call a function
        print(magenta('\--> CALL  A SUB FUNCTION :',bold=True))                  
        relationship=create_relationship_object(sighting_transient_id,incident_xid,relationship_xid,"member-of","DevNet Ignit Lab")    # call a function
        relationships_new.append(json.loads(relationship)) # adding this relationship to  relationship list   
    print('\n sightings :\n ',cyan(sightings,bold=True))
    print('\n relationships :\n ',cyan(relationships_new,bold=True))
    #
    # = Create sighting + relationship json payloads from sithging list given as input : OK DONE
    #       
    print(green('\nOK DONE : Create sighting + relationship json payloads from sithging list given as input ',bold=True))
    print(yellow('\nNEXT : Create judgment payload for the malicious observable and attach it to Indicator... then it will be added to the feed =>',bold=True))      
    a = input('type Enter : ')             
    # => Create judgment payload for the malicious observable and attach it to Indicator... then it will be added to the feed :
    #     
    print(yellow("\n- create a judgment JSON payload for the ip source",bold=True))
    judgments_new=[]
    add_a_jugdment_for_source_ip=1 # 1 = we create a judgment for the source IP address, 0 = No we don't create a judgdment
    if add_a_jugdment_for_source_ip==1:
        judgments_new.append(create_judgment_json(ip_source))
        print('\n judgments_new :\n ',cyan(judgments_new,bold=True)) 
        print(yellow("\n- OK Done ",bold=True))  
        print(yellow("\n- Now add a relationship for this judgment to related indicator",bold=True))
        indicator_id=indicator_list[0] 
        print('\nindicator_id : ',cyan(indicator_id,bold=True))        
        relationship_xid=generate_relationship_xid(judgments_new[0]['id'],indicator_id)   # call a function
        relationship_object={}    
        relationship_object = create_relationship_object(judgments_new[0]['id'], indicator_id, relationship_xid, "element-of","DevNet Ignite Labr") # call a function
        print('\n New relationship_object to add into list :\n ',yellow(relationship_object,bold=True)) 
        relationships_new.append(json.loads(relationship_object)) # adding this relationship to  relationship list   
    print('\n final relationship list :\n ',yellow(relationships_new,bold=True))
    #
    # => Create judgment payload for the malicious observable and attach it to Indicator = OK Done
    # 
    print(green('\nOK DONE :  Create judgment payload for the malicious observable and attach it to Indicator ',bold=True))
    print(yellow('\nNEXT : Create the bundle JSON Payload => ',bold=True))      
    a = input('type Enter : ')       
    #
    # => Create the bundle Payload :
    #     
    source_for_bundle="DevNet Ignit Lab"
    print(yellow("\n- Step 6 create Bundle JSON payload => Put everything together",bold=True))    
    #incidents=[]
    indicators=[]
    #relationships_new=[]          
    print(magenta('\n--> CALL  A SUB FUNCTION :',bold=True))           
    bundle=create_bundle_json(source_for_bundle,incidents,sightings,indicators,judgments_new, relationships_new) # call a function
    print(yellow("\n  - Ok Bundle JSON payload is ready",bold=True))
    print(yellow("\n OKAY Ready to create the Incident In destination XDR tenant",bold=True))
    print(yellow("\nStep 7 Let's go !",bold=True))
    bundle_in_json=json.dumps(bundle,indent=4,sort_keys=True, separators=(',', ': '))
    print(cyan('\n'+bundle_in_json,bold=True))  
    print('\nBUNDLE TO BE POSTED IS ABOVE :\n')   
    #
    # => Create the bundle Payload : Ok Done
    #     
    print(green('\nOK DONE : Create the bundle Payload ',bold=True))
    print(yellow('\nNEXT : POST THE BUNDLE TO XDR => ',bold=True))       
    a = input('type Enter : ')     
    print()  
    print('\nOK NOW WE POST THE BUNDLE TO XDR :\n')
    #
    # Let's read the Token We created prior:
    # 
    with open('./ctr_token.txt') as file:
        access_token=file.read()
    resultat=post_bundle(bundle_in_json,access_token,host)
    print('\n Bundle API call result : \n',green(resultat,bold=True)) 
    print(yellow("\n- OK API CALL SENT TO XDR... Check if the Incident had been created ",bold=True))  
    print()    
    env.level=env.level[:-1]
    return(resultat)
  
#  def_current_date_time***
def current_date_time():
    '''
    MODIFIED : 2025-07-20

    description : current time in the YYYY-mm-ddTH:M:S.fZ format
    '''
    route="/current_date_time"
    env.level+='-'
    print('\n'+env.level,white('def current_date_time() : in parse_log_and_create_incident.py >',bold=True))
    current_time = datetime.utcnow()
    current_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    env.level=env.level[:-1]
    return(current_time)
    
#  def_create_incident_json***
def create_incident_json(incident_title,description,source,short_description,tlp,confidence,severity,techniques,tactics,asset_score,ttp_score):
    '''
    MODIFIED : 2025-07-20

    description : Create the Incident JSON payload for the bundle
    '''
    route="/create_incident_json"
    env.level+='-'
    print('\n'+env.level,white('def create_incident_json() in parse_log_and_create_incident.py : >',bold=True))
    print(yellow("\n- > Step 1 create_incident_xid",bold=True))
    xid=create_incident_xid()
    date_and_time=dateTime.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(yellow("\n- > Step 2 generate_incident_json",bold=True))
    incident_object = {}
    incident_object["description"] = source
    incident_object["schema_version"] = "1.3.9"
    incident_object["type"] = "incident"
    incident_object["source"] = source
    incident_object["short_description"] = short_description
    incident_object["title"] = incident_title
    incident_object["incident_time"] = { "discovered": date_and_time, "opened": date_and_time }
    incident_object["status"] = "New"
    incident_object["tlp"] = tlp
    incident_object["confidence"] = confidence
    incident_object["severity"] = severity
    incident_object["techniques"] = techniques
    incident_object["tactics"] = tactics
    incident_object["categories"]:[categories[3]]
    incident_object["discovery_method"]:discover_method[2]
    incident_object["promotion_method"]="Automated"
    incident_object["scores"]={}
    incident_object["scores"]["asset"]=asset_score    
    incident_object["scores"]["ttp"]=ttp_score
    incident_object["scores"]["global"]=incident_object["scores"]["asset"]*incident_object["scores"]["ttp"]
    incident_object["id"] = xid    
    incident_json = json.dumps(incident_object)
    payload = json.dumps(incident_object,indent=4,sort_keys=True, separators=(',', ': '))
    #print(response.json())     
    print('\n Incidents JSON :\n',cyan(payload,bold=True))
    env.level=env.level[:-1]
    return(incident_json,xid)
  
    
if __name__=="__main__":
    '''
        version : 2025-09-10
    '''
    print(yellow('\nSTARTING HERE => ',bold=True))       
    print(yellow('\nNEXT : Load connection parameters to XDR Tenant => ',bold=True))  
    #
    # Load API connection details to XDR tenant for futur utilization :
    #    
    with open('config.txt','r') as file:
        text_content=file.read()
    client_id,client_password,host_for_token,host,conure = parse_config(text_content)    
    #
    # Load API connection details to XDR tenant for futur utilization :
    #
    # Ask for an API token to XDR :
    #  
    print(yellow('\nNEXT : Asking for an API token => ',bold=True))    
    a = input('Press Enter : ')        
    access_token=get_ctr_token(host_for_token,client_id,client_password)
    #
    # Ask for an API token to XDR = OK DONE
    #     
    print(yellow('\nNEXT : Read syslog message => ',bold=True))
    a = input('Press Enter : ')    
    #
    # read syslog message :
    #
    with open('./log.log') as file:
        syslog_message=file.read()
    print('\nsyslog_message :',cyan(syslog_message,bold=True))
    print(yellow('\nNEXT : Parse the syslog message above => ',bold=True))     
    a = input('Press Enter : ')         
    #
    # parse the syslog message and get back objects needed for sighting definitions :
    #
    log_objects=parse_syslog(syslog_message) # call function   
    print(green("\n- Parse the syslog message above = OK Done ",bold=True))    
    print(yellow('\nNEXT : Create a sighting list with every parsed detections from syslog =>',bold=True))    
    a = input('Press Enter : ')             
    #
    # create a single sighting json payload to be added into a list that contains all sightings:
    #
    sighting_json=create_a_sighting_json(log_objects) # call function
    #
    # Add it into a sighting list :
    #
    sighting_list=[]
    sighting_list.append(sighting_json)
    print(green("\nCreate a sighting list with every parsed detections from syslog = OK Done ",bold=True))  
    #print(yellow('\nNEXT : Create Incident JSON Bundle and Post it to XDR => >',bold=True))    
    a = input('Press Enter : ')           
    #
    # Create the Incident :
    #
    incident_title="Secure Firewall IPS Alerts for Src : "+log_objects['SrcIP']+" to Dst : "+log_objects['DstIP'] # incident title
    result=create_an_xdr_incident(sighting_list,log_objects['SrcIP'],incident_title) # call function   
    print(result)
    if result:
            print(green("\n- OK ALL DONE. Incident POSTED to XDR. Check this into the XDR Tenant : ",bold=True))
    else:
        print(red("\n- ERROR , SOMETHING WRONG HAPPENED : ",bold=True))

