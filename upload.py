import requests 
import json
import os
from dotenv import load_dotenv
from os.path import join, dirname
import tempfile
import csv
import datetime
from requests.auth import HTTPBasicAuth
from urllib3 import Retry
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter

if os.path.isfile(join(dirname(__file__), '.env')):
    load_dotenv(join(dirname(__file__), '.env'))

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=os.getenv('BACKOFF', 15)
)
Retry.BACKOFF_MAX = os.getenv('BACKOFF_MAX', 60)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

api_headers = {
    "Content-Type": "application/json",
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

try:
    secure_temp_dir = tempfile.mkdtemp()
    routes = json.loads(os.environ['API_ROUTES'])

    for route in routes['routes']:

        url = os.environ['API_BASE'] + route + os.getenv('API_OPT_LIMIT')
        response = http.get(url, auth=HTTPBasicAuth(os.environ['API_KEY'], os.environ['API_SECRET']), headers=api_headers).json()
        full_data = response[route[1:]]
        if 'next_page_url' in response['pagination']:
            while 'next_page_url' in response['pagination']:
                response = http.get(response['pagination']['next_page_url'], auth=HTTPBasicAuth(os.environ['API_KEY'], os.environ['API_SECRET']), headers=api_headers).json()
                full_data.extend(response[route[1:]])
        if len(full_data) < 1:
            continue

        dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(f"{secure_temp_dir}/{route[1:]}.csv","w", encoding='utf8', errors='surrogateescape', newline='') as f:
            writer=csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            
            header = []
            if os.getenv('API_ACCESS_TIMESTAMP', "True") == "True":
                    header.append("api_accessed")
            for key, value in full_data[0].items():
                if type(value) == list:
                    for count, _ in enumerate(range(int(os.getenv('MAX_LENGTH', 6)))):
                        new_column_header = f"{key}_{count}"
                        header.append(new_column_header)
                else:
                    header.append(key)
            writer.writerow(header)

            for record in full_data:
                row = []
                if os.getenv('API_ACCESS_TIMESTAMP', "True") == "True":
                    row.append(dt_string)
                for value in record.values():
                    if type(value) == list:
                        if len(value) < (int(os.getenv('MAX_LENGTH', 6))):
                            while len(value) < (int(os.getenv('MAX_LENGTH', 6))):
                                value.append(None)
                            for v in value:
                                row.append(v)
                        elif len(value) > (os.getenv('MAX_LENGTH', 6)):
                            for v in value[:(int(os.getenv('MAX_LENGTH', 6)))]:
                                row.append(v)
                        else:
                            for v in value:
                                row.append(v)
                    else:
                        row.append(value)
                writer.writerow(row)

except Exception as e:
    print ('Error',e)

try:
    data = {'grant_type':"client_credentials", 
            'resource':"https://graph.microsoft.com", 
            'client_id':f'{os.getenv("M365_CLIENT")}', 
            'client_secret':f'{os.getenv("M365_SECRET")}'} 

    URL = f'https://login.windows.net/{os.getenv("M365_TENANT")}/oauth2/token?api-version=1.0'
    r = requests.post(url = URL, data = data) 
    j = json.loads(r.text)
    TOKEN = j["access_token"]
    headers={'Authorization': "Bearer " + TOKEN}
    
    if os.getenv("M365_ROOT_FOLDER_NAME") is not None:
        URL = f'https://graph.microsoft.com/v1.0/users/{os.getenv("M365_USER_ID")}/drive/root/children'
        m365_response = requests.get(URL, headers=headers).json()
        for item in m365_response['value']:
            if 'folder' in item.keys():
                if item['name'] == os.getenv("M365_ROOT_FOLDER_NAME"):
                    folder_id = item['id']
        URL = f'https://graph.microsoft.com/v1.0/users/{os.getenv("M365_USER_ID")}/drive/items/{folder_id}:'
    else:
        URL = f'https://graph.microsoft.com/v1.0/users/{os.getenv("M365_USER_ID")}/drive/root:'

    m365_response = requests.get(URL, headers=headers).json()
    for root, dirs, files in os.walk(secure_temp_dir):
        for filename in files:
            filepath = os.path.join(root,filename)
            print("Uploading "+filename+"...")
            fileHandle = open(filepath, 'rb')
            m365_response = requests.put(URL+"/"+filename+":/content", data=fileHandle, headers=headers)
            fileHandle.close()
            if m365_response.status_code == 200 or m365_response.status_code == 201:
                print("Succeess, removing original file...")
                os.remove(os.path.join(root, filename))
    print("Script completed")

except Exception as e:
    print ('Error',e)