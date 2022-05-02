'''
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

'''
from flask import Flask, render_template, send_from_directory, request, redirect, session, url_for
from requests_oauthlib import OAuth2Session
from webexteamssdk import WebexTeamsAPI
import random
import time
import os
import snow_helper
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

#Global Variables
CURRENT_HOST_IP="0.0.0.0"
CURRENT_PORT=5003

REDIRECT_URI = 'https://'+CURRENT_HOST_IP+':'+str(CURRENT_PORT)+'/callback'

app = Flask(__name__)
app.secret_key = os.urandom(24)

GUEST_ISSUER_SECRET = os.environ.get('GUEST_ISSUER_SECRET')
GUEST_ISSUER_ID = os.environ.get('GUEST_ISSUER_ID')

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

BOT_TOKEN = os.environ.get('BOT_TOKEN')

OAUTH_URL_DOMAIN = os.environ.get('OAUTH_URL_DOMAIN')
AUTHORIZATION_BASE_URL = 'https://'+ OAUTH_URL_DOMAIN +'/v1/authorize'
TOKEN_URL = 'https://'+ OAUTH_URL_DOMAIN +'/v1/access_token'
SCOPE = 'spark:all'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

EXPERTS=[
    'xxx@xxx.com', 
    'xxx@mxxx.com'
    ]

REALWEAR_HEADSET_ACCOUNT_MAPPING={
    '[Production] Realwear Headset 1':'xxx@mxxx.com',
    '[Production] Realwear Headset 2':'xxx@xxx.com',
    '[Production] Realwear Headset 3':'xxx@xxx.com',
    '[Logistics] Realwear Headset 1':'xxx@xxx.com',
    }

SUPPORTED_DEVICES=[
    {"model": "164455",
     "name": "3D Printer",
     "purchased": "April 13, 2018",
     "notes":"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas leo dui, tempus eget enim at, ornare dapibus urna. Vestibulum sed cursus felis. Integer tincidunt sapien justo, sed euismod ante consequat ac. Sed tincidunt risus quis justo laoreet fermentum. Integer nec ex dui. Nulla condimentum felis et erat egestas facilisis. Vivamus auctor, metus eu euismod mattis, velit odio dapibus diam, nec tempor tellus urna eu felis. Vestibulum molestie egestas leo, vitae volutpat neque sollicitudin efficitur. Donec vulputate a odio sit amet aliquam. Suspendisse consectetur feugiat nibh in rhoncus. Quisque sed faucibus tellus, non faucibus lectus. Mauris ullamcorper vel felis nec faucibus.",
     "interface":"static/imgs/dials.png",
     "schematic":"static/imgs/schematic.png",
     "filament_info": "static/imgs/filament.png"
    }
]

consultation_sessions=[]
'''
Automatically stores all sessions and their associated information:
consultation_room_id=string,
expert=string,
worker_name=string,
realwear_headset=string,
device=string,
consultation_ticket_sys_id=string,
call_me_option=bool
'''

# Helpers
def get_webex_person_or_none(api, email):
    '''
    Returns the webex information for a specific person based on their emailaddress.
    If the person doesn't exist none is returned.
    '''
    people = api.people.list(email=email)
    person_details = None

    for person in people:
        person_details = person

    return person_details


def get_model_details_or_none(model_number):
    '''
    Returns the information about a supported device based on a model number.
    If the model number doesn't exist none is returned.
    '''
    global SUPPORTED_DEVICES
    model_details = None
    
    for model in SUPPORTED_DEVICES:
        if model_number == model['model']:
            model_details = model
            break

    return model_details


def get_consultation_session_or_none(expert_email):
    '''
    Returns the information for the first consultation session for an specific expert based his email address.
    If no associated session is available, none is returned.
    '''
    global consultation_sessions
    first_associated_session = None
    
    for session in consultation_sessions:
        if session['expert_email'] == expert_email:
            first_associated_session = session
            break

    return first_associated_session


def clean_consultation_sessions():
    '''
    Removed all saved consulation sessions
    '''
    global consultation_sessions

    consultation_sessions = []


def remove_consultation_session(expert_email, consultation_ticket_sys_id):
    '''
    Removed the information for a specific consultation based the consultation_ticket_sys_id
    '''
    global consultation_sessions
    first_associated_session = None
    
    for session in consultation_sessions:
        if session['consultation_ticket_sys_id'] == consultation_ticket_sys_id:
            consultation_sessions.remove(session)
            break


'''
Returns string with all messages of a specific room. Files are replaces with **File** texts.
'''
def get_chat_history_string(api, room):
    
    # Get chat history
    space_messages = api.messages.list(room)
    space_members = api.memberships.list(room)

    # Create email to displayname mapping since messages returned only contain email addresses of authors
    member_dict = dict()
    for member in space_members:
        email = member.personEmail
        displayName = member.personDisplayName
        member_dict.update({email : displayName})

    # Create single string with all messages and authors displaynames
    messages_string = ""
    for message in reversed(list(space_messages)):
        if message.text != None:
            messages_string = messages_string + f"{member_dict[message.personEmail]} : \n {message.text} \n \n"
        #add placeholders in message_string for files. Files are not yet transfered to snow.
        if message.files != None:
            messages_string = messages_string + f"{member_dict[message.personEmail]} : \n ** Removed file** \n \n"

    return messages_string


#Shared Routes
@app.route('/')
def menu():
    '''
    Route for view that offers links to the worker and expert interface.
    '''
    return render_template("menu.html")

    
#Frontline Worker Routes
@app.route('/worker_initial_form')
def app_start():
    '''
    Route for initial form for frontline worker. 
    Prompts worker name and optional Webex On Demand device and call request option.
    '''
    return render_template("worker_initial_form.html", realwear_headset_account_mapping=REALWEAR_HEADSET_ACCOUNT_MAPPING)


@app.route('/worker_index')
def app_index():
    '''
    Route for view with application functions: Scan QR Code, Expert directory, etc.
    Only the QR code functionality is implemented.
    '''
    try:
        return render_template("worker_index.html")

    except Exception as e: 
        print(e)
        return render_template("/worker_initial_form",realwear_headset_account_mapping=REALWEAR_HEADSET_ACCOUNT_MAPPING, error=True, errormessage=e)


@app.route('/worker_scanner')
def app_scanner():
    '''
    Route for scanner. Opens a page with camera view with qr code scanner.
    '''
    try:
        return render_template("worker_scanner.html")

    except Exception as e: 
        print(e)
        return render_template("worker_index.html", error=True, errormessage=e)


@app.route('/worker_expert_choice')
def app_expert_choice():
    '''
    Route with view of available experts and device information.
    Queuing mechanism is not implemented. 
    '''
    global BOT_TOKEN

    try:
        worker_name = request.args.get('worker_name')
        realwear_headset = request.args.get('realwear_headset')
        call_me_option = request.args.get('callme')
        model_number = request.args.get('model')

        model_details = get_model_details_or_none(model_number)

        print("In /queue worker: ", worker_name, "with Webex Expert Device: ", realwear_headset, ", Model ", model_details, " and call option choice ", call_me_option)

        bot_api = WebexTeamsAPI(access_token=BOT_TOKEN)

        experts = []
        for expert_email in EXPERTS:
            expert = get_webex_person_or_none(bot_api, expert_email)
            if expert is not None:
                experts.append(expert)


        return render_template("worker_expert_choice.html", experts=experts, model=model_details, worker_name=worker_name, realwear_headset=realwear_headset, callme=call_me_option)
    
    except Exception as e: 
        print(e)
        return render_template("worker_index.html", error=True, errormessage=e)

@app.route('/worker_chat')
def app_chat():
    '''
    Route for view with Chat window between worker and expert.
    '''
    global BOT_TOKEN

    try: 
        worker_name = request.args.get('worker_name')
        realwear_headset = request.args.get('realwear_headset')
        callme = request.args.get('callme')
        model_number = str(request.args.get('model_number'))
        expert_email = request.args.get('expert')
        
        model_details = get_model_details_or_none(model_number)
        model_name = str(model_details['name'])

        bot_api = WebexTeamsAPI(access_token=BOT_TOKEN)

        expert_details = get_webex_person_or_none(bot_api, expert_email)
        expert_displayname = expert_details.displayName
        if expert_displayname is None:
            expert_displayname = expert_email

        # Create guest issuer
        subject = f"{worker_name}-{random.getrandbits(128)}" # The subject is initialized with a large random number to ensure uniqueness
        worker_name = f"{worker_name}"
        exp = str(int(time.time() + 3600)) # Make the gi valid for one hour
        guest_issuer = bot_api.guest_issuer.create(subject, worker_name, GUEST_ISSUER_ID, exp, GUEST_ISSUER_SECRET)

        # Create SNOW incident
        ticket_impact = 2  # 2 correlates to medium
        ticket_urgency = 2
        ticket_desc = f"{worker_name} requested help from {expert_displayname} for the device {model_name}({model_number}) via the Webex Expert Assistant Application."
        ticket_short_desc = f"[Webex Expert Assistant Integration] Device: {model_name}, Requester: {worker_name}, Requested Expert: {expert_displayname}"
        ticket_response = snow_helper.create_incident(ticket_impact, ticket_desc ,ticket_urgency ,ticket_short_desc)

        print(ticket_response)
        ticket_id = ticket_response['result']['task_effective_number']
        consultation_ticket_sys_id = ticket_response['result']['sys_id']

        # Create space, memberships and initial text
        guest_api = WebexTeamsAPI(access_token=guest_issuer.token)  # Create a api for this guest user to create the space

        room_title = f"Ticket: {ticket_id}, Device: {model_name}({model_number})"
        room = guest_api.rooms.create(room_title) 
        
        guest_api.memberships.create(room.id, personEmail=expert_email)
        if realwear_headset != "":
            realwear_headset_email = REALWEAR_HEADSET_ACCOUNT_MAPPING[realwear_headset]
            guest_api.memberships.create(room.id, personEmail=realwear_headset_email)

        theMessageText="Hi, I need assistance with the device: " + model_name + " (Model: " + model_number +"). "
        if callme == 'true':
            theMessageText = theMessageText + "I want to use my Webex Expert on Demand device for the consultation. Please call me."
        
        guest_api.messages.create(roomId=room.id,text=theMessageText)
        
        #Remove all former consulation session, since this PoV only support one session for demo purposes
        clean_consultation_sessions()

        #Save consultation session info
        consultation_session = {
                'consultation_room_id': room.id, 
                'expert_email': expert_email, 
                'worker_name': worker_name, 
                'guest_issuer_token': guest_issuer.token,
                'realwear_headset': realwear_headset,
                'device': model_details,
                'consultation_ticket_sys_id': consultation_ticket_sys_id,
                'call_me_option': callme
            }
        consultation_sessions.append(consultation_session)

        return render_template("worker_chat.html", guest_token=guest_issuer.token, space_id=room.id)
    
    except Exception as e: 
        print(e)
        return render_template("worker_index.html", error=True, errormessage=e)


#Expert Routes
@app.route("/expert_consult")
def consult():
    '''
    Route for consulation view. Includes chat window, serviceNow ticket functionalities.
    '''
    try:
        teams_token = session['oauth_token']
        access_token = teams_token['access_token']        
        expert_api = WebexTeamsAPI(access_token=access_token)
        
        expert = expert_api.people.me()
        consultation_session = get_consultation_session_or_none(expert.emails[0])

        if consultation_session == None:
            error_message = "No consultation request for the expert " + expert.displayName + " available so far. Please start with the frontline worker workflow to create a consultation request for this specific expert."
            return render_template("menu.html", error=True, errormessage=error_message)

        else:
            consultation_ticket_sys_id = consultation_session['consultation_ticket_sys_id']
            consultation_room_id = consultation_session['consultation_room_id']
            device_details = consultation_session['device']

            #Send initial auto message
            files = []
            if consultation_session['call_me_option'] == 'true':
                theMessageText="Hi, thanks for you patience. I will now look into your request and call you afterwards."
            elif consultation_session['realwear_headset'] != '':
                theMessageText="Hi, thanks for you patience. I will now look into your request. Your Webex on Demand device was automatically added to this space and can thereby be used during the consultation."
            else:
                theMessageText="Hi, thanks for you patience. I will now look into your request. Did you know, we also support consulations with a Webex Expert Device. More information about Webex Expert can be found in the following file:"
                instruction_file = [ os.getcwd()+"/Cisco_Webex_Expert_On_Demand.pdf" ]
            
            expert_api.messages.create(roomId=consultation_room_id, text=theMessageText, files=files)
                
            #Update SNOW ticket
            work_notes = f"{expert.firstName} {expert.lastName} started interacting with requester via Webex Expert Assistant App."
            ticket_response = snow_helper.update_incident_stage(consultation_ticket_sys_id ,2, work_notes) #2 is in progress
            print(ticket_response)

            ticket_link = os.environ.get('SERVICENOW_INSTANCE') + '/nav_to.do?uri=%2Fincident.do%3Fsys_id%3D' + consultation_ticket_sys_id

            return render_template("expert_consult.html", expert=expert, WEBEX_ACCESS_TOKEN=access_token,
                                SPACE_ID=consultation_session['consultation_room_id'], ticket_link=ticket_link, device_details=device_details )
    
    except Exception as e: 
        print(e)
        return redirect("/oauth")


@app.route('/expert_close')
def close():
    '''
    Route to close a interaction and do all associated step.
    '''
    state = request.args.get('state') # 6 for resolved, 7 for closed

    try:

        teams_token = session['oauth_token']
        access_token = teams_token['access_token']
        expert_api = WebexTeamsAPI(access_token=access_token)
        
        expert = expert_api.people.me()
        consultation_session = get_consultation_session_or_none(expert.emails[0])
        consultation_room_id = consultation_session['consultation_room_id']
        consultation_ticket_sys_id = consultation_session['consultation_ticket_sys_id']

        # Send final auto message
        theMessageText="Thanks for using our service. I will close this conversation as requested. Always feel free to reach out again in case we can help."
        expert_api.messages.create(roomId=consultation_room_id, text=theMessageText)

        # Retrieve chat history of consulation room
        messages_string = get_chat_history_string(expert_api, consultation_room_id)

        # Close/Resolve SNOW case
        work_notes = f"{expert.firstName} {expert.lastName} closed/resolved this incident manually via Webex Expert Assistant App."
        ticket_response = snow_helper.close_incident(consultation_session['consultation_ticket_sys_id'], state, work_notes, messages_string) # 6 for resolved, 7 for closed
        print(ticket_response)

        # Remove space
        expert_api.rooms.delete(consultation_room_id)

        # Remove consulation info from consultation_session
        remove_consultation_session(expert, consultation_ticket_sys_id)

        return render_template("menu.html")

    except Exception as e: 
        print(e)
        return render_template("/menu", error=True, errormessage=e)


@app.route("/oauth")
def oauth():
    """Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Webex Teams)
    using a URL with a few key OAuth parameters.
    """
    global CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
    print("starting... with CLIENT_ID: ",CLIENT_ID)
    print("client secret: ",CLIENT_SECRET)
    teams = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = teams.authorization_url(AUTHORIZATION_BASE_URL)

    # State is used to prevent CSRF, keep this for later.

    session['oauth_state'] = state
    print("calling redirect....")
    return redirect(authorization_url)

'''
Step 2: User authorization, this happens on the provider.
'''

@app.route("/callback", methods=["GET"])
def callback():
    """
    Step 3: Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    global CLIENT_ID, CLIENT_SECRET, TOKEN_URL

    print("Client ID: ",CLIENT_ID)
    print("Client secret: ",CLIENT_SECRET)

    try:
        auth_code = OAuth2Session(CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)
        token = auth_code.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET,
                                    authorization_response=request.url)

        """
        At this point you can fetch protected resources but lets save
        the token and show how this is done from a persisted token
        """
        session['oauth_token'] = token
        return redirect("/expert_consult")

    except Exception as e: 
        print(e)
        return redirect("/oauth")
    


if __name__ == "__main__":

    app.run(host=CURRENT_HOST_IP, port=CURRENT_PORT, debug=True, ssl_context='adhoc')


