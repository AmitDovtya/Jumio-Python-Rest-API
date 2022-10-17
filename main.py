# imports.
import time
import base64
import json

from api_creds import TOKEN, SECRET, CLIENT_ID, CLIENT_SECRET

import requests
from requests.auth import HTTPBasicAuth


# API credentials.
token = TOKEN  # input your API token here as a string.
secret = SECRET  # input your API secret here as a string.
client_id = CLIENT_ID  # input your API client ID here as a string.
client_secret = CLIENT_SECRET  # input your API client secret here as a string.


# KYX OAUTH 2.0 token
def get_access_token():
    auth_server_url = "https://auth.amer-1.jumio.ai/oauth2/token"
    token_req_payload = {'grant_type': 'client_credentials'}
    token_response = requests.post(auth_server_url,
                                   data=token_req_payload,
                                   auth=(client_id, client_secret))
    return token_response.json()['access_token']


# Creates a new account and a KYX transaction
def create_kyx_account():
    # api-endpoint
    url = "https://account.amer-1.jumio.ai/api/v1/accounts"

    my_headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'amit_test',
                'Authorization': f'Bearer {get_access_token()}'
            }

    body = {
        "customerInternalReference": "CUSTOMER_REFERENCE",
        "workflowDefinition": {
            "key": 10015,
        },
        "userReference": "YOUR_USER_REFERENCE"
    }

    response = requests.post(url=url, data=json.dumps(body), headers=my_headers)
    return response


# REST API request of standalone ID (10015)
def kyx_api(kyx_trx):
    # extract the API URLs from the transaction.
    front_url = kyx_trx['workflowExecution']['credentials'][0]['api']['parts']['front']
    back_url = kyx_trx['workflowExecution']['credentials'][0]['api']['parts']['back']
    finalize_url = kyx_trx['workflowExecution']['credentials'][0]['api']['workflowExecution']

    my_headers = {
        'User-Agent': 'amit_test',
        'Authorization': f'Bearer {get_access_token()}'
    }

    # Upload front image.
    front_upload = [
        ('file', ('DL_front.jpeg', open('Oliver DL Back (1).jpeg', 'rb'), 'image/jpeg'))
    ]
    requests.post(url=front_url, files=front_upload, headers=my_headers)

    # Upload back image.
    back_upload = [
        ('file', ('DL_front.jpeg', open('Oliver DL Back (1).jpeg', 'rb'), 'image/jpeg'))
    ]
    requests.post(url=back_url, files=back_upload, headers=my_headers)

    # finalize the request and return the status of the transaction.
    return requests.put(url=finalize_url, headers=my_headers).status_code


# performNV
def create_transaction(front_side="Oliver DL Back (1).jpeg", back_side="Oliver DL Front (1).png"):
    # api-endpoint
    url = "https://netverify.com/api/netverify/v2/performNetverify"

    # header parameters
    my_headers = {
                    'Accept': 'application/json',
                    'User-Agent': 'amit_test',
                    'Content-Type': 'application/json'
                }

    # encode ID images
    with open(front_side, "rb") as image_front:
        front_encoded = base64.b64encode(image_front.read()).decode()
    with open(back_side, "rb") as image_back:
        back_encoded = base64.b64encode(image_back.read()).decode()

    # json body
    body = {
                "enabledFields": "idNumber,idFirstName,idLastName,idDob,idExpiry,idUsState,idPersonalNumber,idAddress",
                "merchantIdScanReference": "random",
                "customerId": "random",
                "country": "USA", 
                "idType": "PASSPORT",
                "frontsideImage": front_encoded,
                "backsideImage": back_encoded
            }

    # sending post request and returning response as JSON object.
    return requests.post(url=url, data=json.dumps(body), headers=my_headers, auth=HTTPBasicAuth(token, secret)).json()


# V2 Retrieval API: Gets the current status of a transaction.
def get_status(scan_ref):
    # api-endpoint
    url = "https://netverify.com/api/netverify/v2/scans/" + scan_ref

    # Request for checking status of a V2 transaction. Extract status from the response and return it.
    return requests.get(url=url, auth=HTTPBasicAuth(token, secret)).json()['status']


# V2 API: Keeps checking until the transaction is processed.
def check_status(scan_ref):
    time.sleep(5)
    # get the transaction status.
    t_status = get_status(scan_ref)

    # keep checking the status while transaction is not finished.
    while True:
        print(t_status)
        st = get_status(scan_ref)

        # Exit once the transaction is finished.
        if st != 'PENDING':
            return st
        else:
            time.sleep(5)
            continue


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # res = create_transaction()
    # s_ref = res['jumioIdScanReference']
    # print(s_ref)
    # print(check_status(s_ref))

    kyx_tr = create_kyx_account().json()

    status = kyx_api(kyx_tr)
    print(status)
