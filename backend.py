import requests, base64, os, secrets, hashlib, json
from dotenv import load_dotenv
from flask import Flask, redirect, request

load_dotenv()

app = Flask(__name__)

# The Authorization Code Flow with PKCE 
class Auth:
    
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.code_verifier = self.generate_code_verifier() 
        self.code_challenge = self.generate_code_challenge()
        self.token = None
        self.refresh_token = None
        self.load_token()


    #GENERATE A CODE VERIFIER
    def generate_code_verifier(self):
        return secrets.token_urlsafe(64)
    
    # GENERATE A CODE CHALLENGE
    # Once the code verifier has been generated, we must *HASH* it using the SHA256 algorithm. 
    # This is the value that will be sent within the user authorization request.
    def generate_code_challenge(self):
        code_verifier_bytes = self.code_verifier.encode('ascii')
        code_challenge_digest = hashlib.sha256(code_verifier_bytes).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode('ascii').rstrip('=')
        return code_challenge

    
    # GETTING THE AUTHORIZATION URL
    # Endpoint: /authorize, with params including the hashed code challenge
    def get_authorization_url(self):  
        url = 'https://accounts.spotify.com/authorize'
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256',
            'scope': 'user-read-playback-state user-modify-playback-state'
        }
        #print(f"Params: {params}")
        request_url = requests.Request('GET', url, params=params).prepare().url
        return request_url


    def save_token(self):
        #open token.json file, then save self.token and self.refresh toekn to it
        with open('token.json', 'w') as file:
            token_data = {
                "access_token": self.token,
                "refreh_token": self.refresh_token,
            }
            json.dump(token_data, file)
    
    def load_token(self):
        #open json file, read access token and refresh token, load it to self.token and self.refresh tokne
        with open ('token.json', 'r') as file:
            token_data = json.load(file)
            self.token = token_data.get("access_token")
            self.token = token_data.get("refresh_token")
            
    # GETTING THE ACCESS TOKEN
    # Endpoint: /api/token
    # Exchange the authorization code for an access token.       
    def get_token(self, code):      
        url = 'https://accounts.spotify.com/api/token'
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'code_verifier': self.code_verifier
        }
        
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()
        print(f"Response From get_token: {response_data}")  
        
        self.token = response_data.get('access_token')
        self.refresh_token = response_data.get('refresh_token')
        
        self.save_token()
        return self.token
    
    
    # REFRESHING THE ACCESS TOKEN
    # Endpoint: /api/token
    # Refresh the access token
    def refresh_token(self):
        if not self.refresh_token():
            print("No refresh token available")
            return None
        
        url = 'https://accounts.spotify.com/api/token'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token(),
            'client_id': self.client_id,   
        }
        
        response = requests.post(url, data=data)
        response_data = response.json()
        
        if 'access_token' in response_data:
            self.token = response_data.get('access_token')
            self.save_token()
            return self.token 
        self.token = response_data.get('access_token')
        return self.token
    
    def load_token(self):
        

class Search:
    def __init__(self, token):
        self.token = token

# SEARCHING ARTIOST INFORMATION

    # https://developer.spotify.com/documentation/web-api/reference/search
    # Finds artist metadata from artist name
        # @param Type = Artist is very important
    # @Returns a list of artist metadata
        # [ artists 
        #       ...
        #       ...
        #       "items": [  <---- List of artists
        #           "id"
        #           "name"
        #           ...]
        #    ...    ]
    def get_artist_MetaData(self, artist_name):
        url = 'https://api.spotify.com/v1/search'
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "q": artist_name,
            "type": "artist",
            "limit": 1
        }
        
        try:
            res = requests.get(url, headers=header, params=params)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        
        return res.json()['artists']['items']

    def get_artist_id(self, artist_name):
        artist_data = self.get_artist_MetaData(artist_name)
        id = artist_data[0]['id']
        return id
    
    # https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
        # Finds artist id from artist name
        # @Returns a dictionary of the artist's discography 
            # { ...
            #   ...
            #   "items": [  <---- List of albums
            #      "name"
            #      "release_date"
            #      ...]
            # }       
    def get_artist_descography(self, artist_name):
        artist_id = self.get_artist_id(artist_name)
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "include_groups": "album",
            "limit": 10
        }
        try: 
            res = requests.get(url, headers=header, params=params)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        return res.json()['items']
    
    def get_artist_top_tracks(self, artist_name):
        artist_id = self.get_artist_id(artist_name)
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            res = requests.get(url, headers=header)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        return res.json()['tracks']

# SEARCHING TRACK INFORMATION
    # https://developer.spotify.com/documentation/web-api/reference/search/search
    # Finds track metadata from track name and artist name
        # @param Type = Track is very important
    # @Returns a list of track metadata
        # [ tracks 
        #       ...
        #       ...
        #       "items": [  <---- List of tracks
        #           "id"
        #           "name"
        #           ...]
        #    ...    ]
    def get_track_id(self, artist_name, track_name):
        url = 'https://api.spotify.com/v1/search'
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        param = {
            "q": f"track:{track_name} artist:{artist_name}",
            "type": "track",
            "limit": 1
        }
        
        try:
            res = requests.get(url, headers=header, params=param)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        tracks = res.json()['tracks']['items']
        if len(tracks) == 0:
            print("Track not found")
            return None
        return tracks[0]['id']
    
class Player:
    def __init__(self, token):
        self.token = token
        
    def get_devices(self):
        url = 'https://api.spotify.com/v1/me/player/devices'
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                return res.json().get('devices', [])
            else:
                print(f"Error fetching devices: {res.status_code}")
                return None
        except requests.exceptions.RequestException as e: 
            print(e)
            return None


    


        


