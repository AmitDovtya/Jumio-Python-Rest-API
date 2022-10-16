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
            "key": 10013,
        },
        "userReference": "YOUR_USER_REFERENCE"
    }

    response = requests.post(url=url, data=json.dumps(body), headers=my_headers)
    return response


# performNV
def create_transaction(front_side="Oliver DL Back (1).jpeg", back_side="Oliver DL Front (1).png"):
    # api-endpoint
    url = "https://netverify.com/api/netverify/v2/performNetverify"

    # header parameters
    my_headers = {'Accept': 'application/json', 'User-Agent': 'amit_test', 'Content-Type': 'application/json'}

    # encode ID images
    with open(front_side, "rb") as image_front:
        front_b64 = base64.b64encode(image_front.read())
        front_encoded = front_b64.decode()
    with open(back_side, "rb") as image_back:
        back_b64 = base64.b64encode(image_back.read())
        back_encoded = back_b64.decode()

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

    # sending post request and saving response as response object
    response = requests.post(url=url, data=json.dumps(body), headers=my_headers, auth=HTTPBasicAuth(token, secret))

    # extracting response text
    return response


# V2 Retrieval API: Gets the current status of a transaction.
def get_status(scan_ref):
    # api-endpoint
    url = "https://netverify.com/api/netverify/v2/scans/" + scan_ref

    # Request for checking status of a V2 transaction.
    r = requests.get(url=url, auth=HTTPBasicAuth(token, secret))

    # extracting data in json format.
    data = r.json()

    # extract status from the response.
    status = data['status']

    return status


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
    # res = create_transaction().json()
    # s_ref = res['jumioIdScanReference']
    # print(s_ref)
    # print(check_status(s_ref))
    print(create_kyx_account().json())
