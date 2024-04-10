import json
import requests


def Fetch(url: str, way: str, query=None, header=None, data=None):
    if url == None:
        return None
    if way == 'Get':
        response = requests.get(url=url, params=query, headers=header)
        return response.json()
    elif way == 'Post':
        response = requests.post(
            url=url, params=query, headers=header, data=json.dumps(data))
        return response.json()
    elif way == 'Patch':
        response = requests.patch(
            url=url, params=query, headers=header, data=json.dumps(data))
        return response.json()
    elif way == 'Put':
        response = requests.put(
            url=url, params=query, headers=header, data=json.dumps(data))
        return response.json()
    else:
        return None
