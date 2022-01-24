# Webex Expert Assistant


The Webex Expert Assistant application integrates the Webex Widget, Webex Expert on Demand app with Realwear Headset and ServiceNow to create an optimized support workflow for frontline workers and experts. 

It allows frontline workers to request and get help via mobile devices and based on video/messaging/VR sessions. The remote Expert can see device information and data of the faulty device on the same page as the panel for communication with the frontline worker. A ServiceNow integration eases the involved documentation effort.

The sample application is a Flask application that serves as a web application to both, the frontline worker (table or smartphone) and the remote expert (desktop PC or Mac). 

   > Note: This demo is an enhanced and highly adapted version of the former GVE DevNet use case: https://gve-devnet.cisco.com/details/113

## Contacts
* Ramona Renner 


## Pre-requisites
* 1 or more Webex account
* Realwear Headset with Webex Expert on Demand (separate Webex account required)
* ServiceNow instance (developer instance available [here](https://developer.servicenow.com/dev.do)) 
* Firefox or Chrome Browser
* (Optional) IaaS solution to host the code or ngrok to make application reachable via internet accessible URL


## Workflow

### Frontline Worker
![/IMAGES/workflow-worker.png](/IMAGES/workflow-worker.png)

### Expert
![/IMAGES/workflow-expert.png](/IMAGES/workflow-expert.png)

## High-Level Architecture
![/IMAGES/high-level.png](/IMAGES/high-level.png)

This demo allows a frontline worker to easily request help, and choose a specific expert. Therefore, the worker only needs to provide his name, and to scan a QR code on the faulty machine. For each help request, the application automatically creates a guest account, Webex space and ServiceNow incident for communication and documentation purpose. The frontline worker can use the Webex chat or video function or optionally also a VR Realwear Headset during the consultation. 

The expert, on the other side, can log into an expert portal - a portal that provides information about the help request, detailed instructions of the faulty machine, a chat and video function and the options to view, close or resolve a case. Further experts can be easily added to the consultation if required.  
The application automatically updates the ServiceNow incident during the process, and thereby also transfers the Webex chat message history to ServiceNow when the expert closes or resolves the request. 

   > Note: The UI of this sample code includes some static, unimplemented features to show further possibilities e.g. expert queueing feature 

## Installation

1. Make sure you have [Python 3.8.0](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed

2.	(Optional) Create and activate a virtual environment 
    ```
    python3 -m venv [add name of virtual environment here] 
    source [add name of virtual environment here]/bin/activate
    ```

3. Access the created virtual environment folder
    ```
    cd [add name of virtual environment here] 
    ```

4. Clone this Github repository into a local folder:  
  ```git clone [add github link here]```
  * For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
      ![/IMAGES/giturl.png](/IMAGES/giturl.png)
  * Or simply download the repository as zip file using 'Download ZIP' button and extract it

5. Access the downloaded folder:  
    ```cd gve_devnet_Webex_expert_assistant```

6. Install all dependencies:  
  ```pip install -r requirements.txt```

7. Setup or use an existing [Webex Teams Guest Issuer](https://developer.webex.com/docs/guest-issuer) and note the guest issuer ID and secret for a later step.

8. Register a [Webex Teams OAuth integration](https://developer.webex.com/docs/integrations)
    * Set the Redirect URL to: http**s**://0.0.0.0:5003/callback (default) or whatever IP address and port you are using for your server. 
    * Select the 'spark:all' scope
    * Note the client ID and client secret for a later step.

9. Create a [Webex Bot](https://developer.webex.com/docs/bots) 
    * Note the Bot Token for a later step.

10. Configure the environment variables in the **.env** file:  
      
    ``` 
    GUEST_ISSUER_ID="[guest issuer ID from step 7]"
    GUEST_ISSUER_SECRET="[guest issuer secret from step 7]"
   
    CLIENT_ID="[Integration client ID from 8]"
    CLIENT_SECRET="[Integration client secret from 8]"    

    BOT_TOKEN="[Bot token from 9]"

    SERVICENOW_USERNAME="[ServiceNow instance username]"
    SERVICENOW_PASSWORD="[ServiceNow instance passwort]"
    SERVICENOW_INSTANCE="[URL for ServiceNow instance]"
    ```   

    > Note: Mac OS hides the .env file in the finder by default. View the demo folder for example with your preferred IDE to make the file visible.

11. Fill in an email address for each expert (corresponding to a Webex account) by editing the corresponding data structure in the **app.py** file:
    ``` 
    EXPERTS = [
        'WbxTeamsUser1@acme.com',
        'WbsTeamsUser2@acme.com'
    ]
    ``` 

    > Note: For simplicity the first expert in the list corresponds to the **First available Expert** in the queue of experts offered to the frontline worker. 

12. Fill in an email address for each available Realwear Headsets with Webex Expert on Demand (corresponding to a Webex account) by editing the corresponding data structure in the **app.py** file:

    ``` 
    REALWEAR_HEADSET_ACCOUNT_MAPPING={
        '[Production] Realwear Headset 1':'WbxTeamsUser1@acme.com',
        '[Production] Realwear Headset 2':'WbxTeamsUser1@acme.com',
        '[Production] Realwear Headset 3':'WbxTeamsUser1@acme.com',
        '[Logistics] Realwear Headset 1':'WbxTeamsUser1@acme.com',
        } 
    ``` 

13. Run the application

  ```python app.py```


Assuming you kept the default parameters for starting the Flask application, the address to navigate to would be:  
```https://0.0.0.0:5003/```

This page offers a choice between the two personas of this demo.

The direct link to the starting page of each persona is:
* Frontline worker view: ```https://0.0.0.0:5003/worker_initial_form```
* Expert portal: ```https://0.0.0.0:5003/expert_consult```

If you are not running the code with HTTPS using a real certificate, you will need to accept
the warnings generated by the browser on the device. 

It is important to first execute the workflow for the frontline worker, since the page for the expert is only accessible after the worker requested help.


## Additional Steps to Demonstrate the Frontline Worker View on a Seperate Mobile Device

If the frontline worker page should be accessible from a mobile device instead of a separate browser window, the app requires being reachable over an internet accessible URL. Therefore, it can be deployed on different IaaS platform like Heroku, Amazon Web Services Lambda, Google Cloud Platform (GCP) and more. Alternatively, it is possible to use the tool [ngrok](https://ngrok.com) for this reason. Please be aware that ngrok can be blocked in some corporate networks. 

   > Note: Besides the creation of the public URL it is also required to change the **Redirect URL** of the Webex Integration (step 7) and the **REDIRECT_URI** variable in the **app.py** file based on the public URL.

## Tools/Products Used
* Webex Space Widget / Webex Python SDK / Webex Bot / Webex Guest Issuer
* Webex Expert on Demand with Realwear Headset
* Python 3.8
* Flask / Javascript / HTML / CSS

## Useful Resources

 - [Python 3.8.0](https://www.python.org/downloads/)
 - [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
 - [ServiceNow for Developers](https://developer.servicenow.com/dev.do)
 - [Webex for Developers](https://developer.webex.com/)
 - [ngrok](https://ngrok.com)
 
### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
