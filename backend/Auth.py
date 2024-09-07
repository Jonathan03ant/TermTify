import requests
import base64
import os
from dotenv import load_dotenv
from flask import Flask, redirect, request

load_dotenv()

app = Flask(__name__)

class Auth:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.token = None

    def get_authorization_url(self):
        url = 'https://accounts.spotify.com/authorize'
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'user-read-playback-state user-modify-playback-state'
        }
        request_url = requests.Request('GET', url, params=params).prepare().url
        return request_url

    def get_token(self, code):
        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()
        self.token = response_data.get('access_token')
        return self.token