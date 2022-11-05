# pythonRestAPI

## Overview

This script is implenentated in Python. It includes several function to create and check transaction status.

## Requirements

+ Python 3.10
+ Requests library 2.28.1

## Functions

Below are the fuctions related to the different API platforms:

### KYX and V3 API
+ get_access_token: Returns an OAuth 2.0 token to authenticate KYX or V3 API requests.
+ get_access_token_2(): Returns an OAuth 2.0 token to authenticate KYX or V3 API requests. Alternative for get_access_token() using:
    from oauthlib.oauth2 import BackendApplicationClient
    from requests_oauthlib import OAuth2Session
+ create_kyx_account: Creates a new KYX account ID for the provided Workflow key and returns the response in JSON format, which includes Account ID and Transaction reference.
+ kyx_api: Receives a KYX response in JSON format and completes the request through API platform and returns the response.
+ retrieve_facemap: Retrieves facemap from an existing account using account and workflow IDs. It will create a 'facemap.bin' file in the current folder with the facemap.
+ authentication_on_premise: For an existing account with liveness, it will use existing facemap and will generate a web URL to complete the Authentication.
+ get_status_v3_kyx: It will return the status for the provided account and workflow ID.
+ check_status_v3_kyx: It will keep checking the status until the transaction is finished. Returns the final status for the provided account and workflow ID.

### V2 API
+ create_transaction: It will do a performNV (ID only) transaction for the provided ID images (jpeg or png). It will return the response for the completed request in JSON format.
+ get_status: It will return the status for the provided scan reference.
+ check_status(scan_ref): It will keep checking the status until the transaction is finished. Returns the final status for the provided scan reference.

## Running the script
Remove the following import statement:
```
from api_creds import TOKEN, SECRET, CLIENT_ID, CLIENT_SECRET
```

Add your API credentials:
```
token = TOKEN  # input your API token here as a string.
secret = SECRET  # input your API secret here as a string.
client_id = CLIENT_ID  # input your API client ID here as a string.
client_secret = CLIENT_SECRET  # input your API client secret here as a string.
```
** Remove or comment out the API credentials for the unused platform.

Chechout the main() function for the test requests or add your own code to create requests using the functions.
