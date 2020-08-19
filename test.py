import json
import requests

headers = {
           # "Authorization": 'Bearer {}'.format(KEYS[COMPANY]),
           "Content-type": "application/json",
           "accept": "application/json",
           }
# headers = {
#            "Authorization": "zoaNO5cOOkWErV5MzMkljjOG3d5Gywm6AicjA0TC909S60fryzyo8qYsksS5CvIU4CwKvIDX6A81yXbZ",
#            }
api_url = 'http://localhost:8000/files/'

params = {
          "download": 6,
}

request = json.dumps(params)

response = requests.post(api_url, headers=headers, data=request)
print(response)
print(response.text)
res = response.json()
print(res)
