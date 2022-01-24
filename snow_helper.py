"""
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from webexteamssdk import WebexTeamsAPI
import requests
import os
import re
import json
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

HEADERS = {"Content-Type":"application/json", "Accept":"application/json"}
AUTH = (os.environ['SERVICENOW_USERNAME'], os.environ['SERVICENOW_PASSWORD'])


'''
Creates a new incident in Service now.
'''
def create_incident(impact,desc,urgency,vmanage_alert_id):
    try:
        servicenow_caller = requests.get(os.environ['SERVICENOW_INSTANCE'] + "/api/now/table/sys_user?sysparm_query=user_name%3D" + os.environ['SERVICENOW_USERNAME'], auth=AUTH, headers=HEADERS).json()['result'][0]['name']
    except Exception:
        raise Exception("Cannot Get ServiceNow CallerID! Check Variables and ServiceNow availability.")
    ticket = {
        "caller_id": servicenow_caller,
        "impact": impact,
        "urgency": urgency,
        "short_description": vmanage_alert_id,
        "description": "The full log for this alert is:  \n" + desc
    }
    try:
        create_ticket = requests.post(os.environ['SERVICENOW_INSTANCE'] + "/api/now/table/incident", auth=AUTH, headers=HEADERS, json=ticket)
    except Exception as e:
        raise Exception("Error on Getting ServiceNow Incidents! Check your ServiceNow settings, availability or connectivity.")

    servicenow_raw_json = create_ticket.json()

    return servicenow_raw_json


'''
Closes or resolves a ServiceNow incident
'''
def close_incident(sys_id, state, work_notes, close_notes): # state:6 is for resolved

    data = {
        "incident_state": state,
        "state": state,
        "work_notes": work_notes,
        "close_notes": close_notes
    }
    try:
        incident = requests.put(os.environ['SERVICENOW_INSTANCE'] + "/api/now/table/incident/" +sys_id, auth=AUTH, headers=HEADERS, json=data)
    except Exception:
        raise Exception("Error on Getting ServiceNow Incidents! Check your ServiceNow settings, availability or connectivity.")

    servicenow_raw_json = incident.json()["result"]

    return incident.status_code


'''
Updates an ServiceNow incident
'''
def update_incident_stage(sys_id, state, work_notes):

    data = {
        "incident_state": state,
        "state": state,
        "work_notes": work_notes
        }
    try:
        incident = requests.put(os.environ['SERVICENOW_INSTANCE'] + "/api/now/table/incident/" +sys_id, auth=AUTH, headers=HEADERS, json=data)
    except Exception:
        raise Exception("Error on Getting ServiceNow Incidents! Check your ServiceNow settings, availability or connectivity.")

    servicenow_raw_json = incident.json()["result"]

    return incident.status_code


'''
Returns an ServiceNow indicent with an secific short description
'''
def get_incident(short_desc): 

    try:
        incident = requests.get(os.environ['SERVICENOW_INSTANCE'] + "/api/now/table/incident", auth=AUTH, headers=HEADERS)
    except Exception as e:
        raise Exception("Error on Getting ServiceNow Incidents! Check your ServiceNow settings, availability or connectivity.")

    servicenow_raw_json = incident.json()["result"]
    for items in servicenow_raw_json:
        if items['short_description'] == str(short_desc):
            print(items)
            return items['sys_id']
    return servicenow_raw_json
