# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : functions for feed indicator judgment script
'''
import requests
import json
import sys
from datetime import datetime, date, timedelta
import hashlib
from crayons import *
import env as env


#  def_create_judgment_external_id***
def create_judgment_external_id(judgment_input):
    '''
    MODIFIED : 2025-07-20

    description : Create an external ID for judgement which is required within the Bundle
    '''
    route="/create_judgment_external_id"
    env.level+='-'
    print('\n'+env.level,white('def create_judgment_external_id() in functions_for_feeds_indicators_and_judgments.py : >\n',bold=True))
    # hash judgment without transient ID
    hash_input = json.dumps(judgment_input)
    hash_value = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    judgment_external_id = "xdr-automation-judgment-" + hash_value
    env.level=env.level[:-1]
    return judgment_external_id
    
#  def_create_relationship_json_payload***
def create_relationship_json_payload(relationship_object,source_xid, target_xid, relationship_xid):
    '''
    MODIFIED : 2025-07-20

    description : create the relationships JSON payload to be added into the bundle
    '''
    route="/create_relationship_json_payload"
    env.level+='-'
    print('\n'+env.level,white('def create_relationship_json_payload() in functions_for_feeds_indicators_and_judgments.py : >\n',bold=True))
    relationship_object["external_ids"] = [relationship_xid]
    relationship_object["source_ref"] = source_xid
    relationship_object["target_ref"] = target_xid
    relationship_object["source"] = "Cisco XDR Automation"
    relationship_object["relationship_type"] = "element-of"
    relationship_object["type"] = "relationship"
    relationship_object["id"] = "transient:"+relationship_xid
    env.level=env.level[:-1]
    return 1
  
#  def_generate_relationship_xid***
def generate_relationship_xid(source_xid, target_xid):
    '''
    MODIFIED : 2025-07-20

    description : Create a relationship transiant ID which is required for the bundle
    '''
    route="/generate_relationship_xid"
    env.level+='-'
    print('\n'+env.level,white('def generate_relationship_xid() in functions_for_feeds_indicators_and_judgments.py : >\n',bold=True))
    hash_value = hashlib.sha1((source_xid + target_xid).encode('utf-8'))
    hash_value = hash_value.hexdigest()
    relationship_xid = "xdr-automation-relationship-" + hash_value
    env.level=env.level[:-1]
    return relationship_xid
  
if __name__=="__main__":
    print("start here")
