import logging
import requests
from urllib.parse import urljoin


def v1_payload(secret_key, secret_value):
    return {'name': secret_key,
            'data': secret_value,
            'pull_request': False}


def v0_payload(secret_key, secret_value):
    return {'name': "" + secret_key,
            'value': "" + secret_value,
            'event': ['push', 'tag', 'deployment']}


class Drone(object):

    def __init__(self, data=None):
        self.data = data
        self.header = ()
        self.session = None
        self.good_status = [200, 201, 202, 203, 204]
        self.headers = {'Authorization': "Bearer " + self.data['drone']['token']}

    def get(self, secret_key):
        drone_url = urljoin(self.data['drone']['url'], secret_key)

        response = requests.get(drone_url,
                                headers=self.headers)
        status_code = response.status_code
        if status_code in self.good_status:
            return response.text
        elif status_code == 401:
            raise Exception(f'**Access denied** Please check the drone credentials for {drone_url}')
        return None

    def delete(self, secret_key):
        drone_url = urljoin(self.data['drone']['url'], secret_key)
        logging.info(f"Deleting Key: {secret_key}")
        response = requests.delete(drone_url,
                                   headers=self.headers)
        status_code = response.status_code
        if status_code in self.good_status:
            return response.text
        elif status_code == 401:
            raise Exception(f'**Access denied** Please check the drone credentials for {drone_url}')
        else:
            raise Exception(f'Error: {status_code}: response.txt')

    def post(self, secret_key, secret_value):
        drone_url = self.data['drone']['url']
        drone_version = self.data['drone']['alt_version']
        payload = v0_payload(secret_key, secret_value)
        if drone_version == "v1":
            payload = v1_payload(secret_key, secret_value)
        response = requests.post(drone_url,
                                 json=payload,
                                 headers=self.headers)
        status_code = response.status_code
        if status_code in self.good_status:
            return response.text
        elif status_code == 401:
            raise Exception(f'**Access denied** Please check the drone credentials for {drone_url}')
        else:
            raise Exception(f'Error: {status_code}: response.txt')

    def update(self, secret_key=None, secret_value=None):
        get_response = self.get(secret_key)
        if get_response:
            logging.warning(f'Deleting {secret_key}, as it already exists')
            self.delete(secret_key)
        logging.info(f'Adding: {secret_key} to Drone')
        self.post(secret_key, secret_value)
