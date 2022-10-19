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

    return requests.post(url=url, data=json.dumps(body), headers=my_headers).json()


# REST API request of standalone ID (10015)
def kyx_api(kyx_trx_response):
    # extract the API URLs from the transaction.
    front_url = kyx_trx_response['workflowExecution']['credentials'][0]['api']['parts']['front']
    back_url = kyx_trx_response['workflowExecution']['credentials'][0]['api']['parts']['back']
    finalize_url = kyx_trx_response['workflowExecution']['credentials'][0]['api']['workflowExecution']

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

    # finalize the request and return the response as a dictionary.
    return requests.put(url=finalize_url, headers=my_headers).json()


def retrieve_facemap(account_id, workflow_id):
    # Transaction retrieval URL and headers
    retrieval_url = f"https://retrieval.amer-1.jumio.ai/api/v1/accounts/{account_id}/workflow-executions/{workflow_id}"
    retrieval_headers = {
        'User-Agent': 'amit_test',
        'Authorization': f'Bearer {get_access_token()}'}

    # download facemap and write to a filename facemap.bin
    facemap_response = requests.get(url=retrieval_url, headers=retrieval_headers).json()
    facemap_url = facemap_response['capabilities']['liveness'][0]['validFaceMapForAuthentication']
    facemap_download = requests.get(url=facemap_url, headers=retrieval_headers)
    with open('facemap.bin', 'wb') as facemap:
        facemap.write(facemap_download.content)


# V3 API: Authentication - Facemap on premise
def authentication_on_premise(account_id="2797b914-d9e9-4c1c-ae5d-d84f062d8920",
                              workflow_id="0909c43c-949c-4a5e-8b1c-090e673d400f"):
    retrieve_facemap(account_id, workflow_id)  # Create/ overwrite facemap.bin file with required facemap binary stream.

    # api-endpoint
    url = f"https://account.amer-1.jumio.ai/api/v1/accounts/{account_id}"

    my_headers = {
        'User-Agent': 'amit_test',
        'Authorization': f'Bearer {get_access_token()}',
        'Content-type': 'application/json'
    }

    facemap_headers = {
        'User-Agent': 'amit_test',
        'Authorization': f'Bearer {get_access_token()}'
    }

    body = {
        "customerInternalReference": "CUSTOMER_REFERENCE",
        "workflowDefinition": {
            "key": 16,
        },
        "userReference": "YOUR_USER_REFERENCE"
    }

    response = requests.put(url=url, headers=my_headers, data=json.dumps(body)).json()
    web_link = response['web']['href']
    facemap_link = response['workflowExecution']['credentials'][1]['api']['parts']['facemap']
    file = [
        ('file', ('facemap.bin', open('facemap.bin', 'rb'), 'application/octet-stream'))
    ]

    # return request status and the web URL to capture face.
    return requests.post(url=facemap_link, files=file, headers=facemap_headers).status_code, web_link


# Get status of a V3 or KYX transaction.
def get_status_v3_kyx(account_id, workflow_id):
    retrieval_url = f"https://retrieval.amer-1.jumio.ai/api/v1/accounts/{account_id}" \
                    f"/workflow-executions/{workflow_id}/status"
    retrieval_headers = {
        'User-Agent': 'amit_test',
        'Authorization': f'Bearer {get_access_token()}'}
    retrieval_response = requests.get(url=retrieval_url, headers=retrieval_headers)
    return retrieval_response.json()['workflowExecution']['status']


# Check status until a V3 or KYX transaction is finished.
def check_status_v3_kyx(account_id, workflow_id):
    while True:
        kyx_status = get_status_v3_kyx(account_id, workflow_id)

        # Exit once the transaction is finished.
        if kyx_status != 'INITIATED':
            return kyx_status
        else:
            print(kyx_status)
            time.sleep(5)
            continue


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
    url = f"https://netverify.com/api/netverify/v2/scans/{scan_ref}"

    # Request for checking status of a V2 transaction. Extract status from the response and return it.
    return requests.get(url=url, auth=HTTPBasicAuth(token, secret)).json()['status']


# V2 API: Keeps checking until the transaction is processed.
def check_status(scan_ref):
    time.sleep(5)

    # keep checking the status while transaction is not finished.
    while True:
        st = get_status(scan_ref)

        # Exit once the transaction is finished.
        if st != 'PENDING':
            return st
        else:
            print(st)
            time.sleep(5)
            continue


def main():
    # call to V2: performNV API
    res = create_transaction()
    print(res['jumioIdScanReference'])
    print(check_status(res['jumioIdScanReference']))

    # call to KYX: Standalone ID Rest API
    kyx_tr = create_kyx_account()  # receives a dictionary with the response parameters of KYX transaction creation.
    response = kyx_api(kyx_tr)
    acc_id = response['account']['id']
    wf_id = response['workflowExecution']['id']
    kyx_tr_status = check_status_v3_kyx(acc_id, wf_id)
    print(kyx_tr_status)

    # call to V3 API: Authentication with facemap on premise. Need to use the link to complete the transaction.
    print(
        authentication_on_premise(account_id="2797b914-d9e9-4c1c-ae5d-d84f062d8920",
                                  workflow_id="0909c43c-949c-4a5e-8b1c-090e673d400f")
    )


if __name__ == '__main__':
    main()
