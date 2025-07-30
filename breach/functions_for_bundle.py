# -*- coding: UTF-8 -*-
#!/usr/bin/env python
'''
    description : manages scripts that manage XDR Bundle API
'''
import requests
import json
import sys
from datetime import datetime, date, timedelta
import hashlib
from crayons import *
import env as env


#  def_create_bundle_json***
def create_bundle_json(source,incidents,sightings,indicators,judgments_new, relationships_new):
    '''
    MODIFIED : 2025-07-20

    description : Create the Bundle JSDON payload to be posted to XDR
    '''
    route="/create_bundle_json"
    env.level+='-'
    print('\n'+env.level,white('def create_bundle_json() in functions_for_bundle.py : >\n',bold=True))
    # ===================================================================    
    bundle_object={}
    bundle_object["type"] = "bundle"
    bundle_object["source"] = source
    if incidents!=[]:
        bundle_object["incidents"] = incidents
    if sightings!=[]:
        bundle_object["sightings"] = sightings
    if indicators!=[]:
        bundle_object["indicators"] = indicators
    if judgments_new!=[]:
        bundle_object["judgements"] = judgments_new
    if relationships_new!=[]:
        bundle_object["relationships"] = relationships_new
    env.level=env.level[:-1]
    return(bundle_object)
#  def_post_bundle***
def post_bundle(json_payload,access_token,host):
    '''
    MODIFIED : 2025-07-29

    description : post the bundle to XDR
    '''
    route="/post_bundle"
    env.level+='-'
    print('\n'+env.level,white('def post_bundle() in functions_for_bundle.py : >\n',bold=True))    
    # #########################################################################################################################
    #
    # API documentation : https://developer.cisco.com/docs/cisco-xdr/private-intelligence-api-bundle-post-many-new-entities-using-a-single-http-call/
    #
    # #########################################################################################################################     
    url=f"{host}/ctia/bundle/import"
    headers = {'Authorization':'Bearer {}'.format(access_token), 'Content-Type':'application/json', 'Accept':'application/json'}
    response = requests.post(url, headers=headers,data=json_payload)
    rep = json.dumps(response.json(),indent=4,sort_keys=True, separators=(',', ': '))
    print(rep)
    if response.status_code==200 or response.status_code==201:
        env.level=env.level[:-1]
        return 1
    elif response.status_code==401: # access token expired or not valid
        # ask for a new token
        access_token=ask_for_a_token()
        # try again
        response = requests.post(url, headers=headers,data=json_payload)
        rep = json.dumps(response.json(),indent=4,sort_keys=True, separators=(',', ': '))
        print(rep)
        if response.status_code==200 or response.status_code==201:
            env.level=env.level[:-1]
            return 1     
        else:
            env.level=env.level[:-1]
            return 0    
    else:
        env.level=env.level[:-1]
        return 0
      

