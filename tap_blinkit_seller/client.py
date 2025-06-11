import requests
import requests_oauthlib
import singer
import singer.metrics
from .config import update_config
import zlib
import json
import time
import os
import re
from dotenv import load_dotenv
import base64

LOGGER = singer.get_logger()  # noqa

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class BlinkitsellerClient:

    MAX_TRIES = 8

    def __init__(self, config):
        self.config = config
        self.access_token = self.get_authorization()

    def get_jwt_token(self):

        response = requests.post("https://fcc.blinkit_seller.co.in/api/v1/auth/sign-in?applicationId=d0cd4873-7cb3-4c7c-9a25-3b109a0d2301", json={
            "email": self.config.get("email"),
            "password": self.config.get("password")
        })

        response_json = response.json()
        # Add identity values to the config
        self.config['jwtToken'] = response_json.get('jwtToken')
        self.config['tokenType'] = response_json.get('tokenType')
        self.config['redirectUrl'] = response_json.get('redirectUrl')
        self.config['userId'] = response_json.get('userId')
        self.config['fullName'] = response_json.get('fullName')
        self.config['contact'] = response_json.get('contact')
        self.config['tags'] = response_json.get('tags')

        # Decode the JWT token
        jwt_parts = response_json.get('jwtToken').split('.')
        if len(jwt_parts) == 3:
            try:
                jwt_payload = jwt_parts[1]
                # Add padding if necessary
                jwt_payload += '=' * (4 - len(jwt_payload) % 4)
                decoded_payload = base64.b64decode(jwt_payload).decode('utf-8')
                self.config['jwtPayload'] = json.loads(decoded_payload)
            except Exception as e:
                LOGGER.warning(f"Could not decode JWT payload: {e}")
        else:
            LOGGER.warning("JWT token does not have the expected structure.")

        update_config(self.config)

    def refresh_token(self):
        refreshed_identity = requests.post(
            "https://securetoken.googleapis.com/v1/token?key=AIzaSyA258Mym_O68D-BQvoK8IUcTlyI0OrEFDQ",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
            "grant_type": "refresh_token",
            "refresh_token": self.config.get('refresh_token')
            }
        )

        LOGGER.info("refreshed_identity", refreshed_identity.json())

        if refreshed_identity.status_code != 200:
            raise RuntimeError(f"Failed to refresh token: {refreshed_identity.text}")
        refreshed_identity_json = refreshed_identity.json()
        self.config['jwtToken'] = refreshed_identity_json.get('id_token')
        self.config['refresh_token'] = refreshed_identity_json.get('refresh_token')
        self.config['expiresAt'] = int(time.time()) + int(refreshed_identity_json.get('expires_in'))
        self.config['localId'] = refreshed_identity_json.get('user_id')
        update_config(self.config)

    def get_authorization(self):
        # jwtToken = self.config.get('jwtToken')
        # if not jwtToken:
        #     LOGGER.info("No jwtToken found, getting new one")
        #     self.get_jwt_token()
        #     return self.config['jwtToken']

        self.get_jwt_token()
        return self.config['jwtToken']

        # token_expiry = self.config.get('expiresAt')
        # if token_expiry and time.time() < token_expiry:
        #     LOGGER.info("Token is still valid")
        #     return self.config.get('jwtToken')
        
        # LOGGER.info("Token expired, refreshing")

        # self.refresh_token()

        return self.config['jwtToken']

    def make_request(self, url, method, params=None, body=None, headers=None, attempts=0):
        LOGGER.info("Making {} request to {} ({})".format(method, url, params))
        
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'Accept': '*'
            }
        elif 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        elif 'Accept' not in headers:
            headers['Accept'] = '*'

        headers["Authorization"] = self.config['jwtToken']

        if method == 'GET':
            body = None

        LOGGER.info(f"Headers: {headers}")

        params_exists = params is not None
        body_exists = body is not None

        if params_exists and body_exists:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=body
            )
        elif params_exists and not body_exists:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params
            )        
        elif body_exists and not params_exists:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=body
            )
        else:
            response = requests.request(
                method,
                url,
                headers=headers
            )

        message = f"[Status Code: {response.status_code}] Response: {response.text}"
        LOGGER.info(message)
        if str(response.status_code) == "400":
            LOGGER.info(f"URL: {url}")
            LOGGER.info(f"Method: {method}")
            LOGGER.info(f"Params: {params}")
            LOGGER.info(f"Headers: {headers}")
            LOGGER.info(f"Body: {body}")

        if attempts < self.MAX_TRIES and response.status_code not in [200, 201, 202]:
            if response.status_code == 401:
                LOGGER.info(f"[Status Code: {response.status_code}] Attempt {attempts} of {self.MAX_TRIES}: Received unauthorized error code, retrying: {response.text}")
                self.access_token = self.get_authorization()
            elif response.status_code == 425:
                # dont make anymore requests
                LOGGER.info("Duplicate request. Stopping")
                return response
            else:
                sleep_duration = 2 ** attempts
                message = f"[Status Code: {response.status_code}] Attempt {attempts} of {self.MAX_TRIES}: Error: {response.text}, Sleeping: {sleep_duration} seconds"
                LOGGER.warning(message)
                time.sleep(sleep_duration)

            return self.make_request(url, method, params, body, headers, attempts+1)

        if response.status_code not in [200, 201, 202]:
            message = f"[Status Code: {response.status_code}] Error {response.text} for url {response.url}"
            LOGGER.error(message)
            raise RuntimeError(message)

        return response

    def make_request_json(self, url, method, params=None, body=None, headers=None):
        return self.make_request(url, method, params, body, headers).json()

    def download_gzip(self, url):
        resp = None
        attempts = 3
        for i in range(attempts + 1):
            try:
                resp = requests.get(url)
                break
            except ConnectionError as e:
                LOGGER.info("Caught error while downloading gzip, sleeping: {}".format(e))
                time.sleep(10)
        else:
            raise RuntimeError("Unable to sync gzip after {} attempts".format(attempts))

        return self.unzip(resp.content)

    @classmethod
    def unzip(cls, blob):
        extracted = zlib.decompress(blob, 16+zlib.MAX_WBITS)
        decoded = extracted.decode('utf-8')
        return json.loads(decoded)
