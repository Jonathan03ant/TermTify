import requests
from dotenv import load_dotenv
import os
import base64
from requests import post

load_dotenv()

class Auth:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.token = self.get_token()
        
    def get_token(self):
        # To get a token, we need to send a POST request to the Spotify API
            # We want to include the following in our request:
                # URL: https://accounts.spotify.com/api/token
                # Headers:
                    # Content-Type: application/x-www-form-urlencoded
                    # Authorization: Basic <base64 encoded client_id:client_secret>
                # Data:
                    # grant_type: client_credentials
     
        url =  "https://accounts.spotify.com/api/token"
        header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        res = requests.post(url,
                           headers = { "Content-Type": "application/x-www-form-urlencoded",
                                       "Authorization": f"Basic {header}"
                           },
                           data = {
                               "grant_type": "client_credentials"
                           })
        token = res.json().get("access_token")
        return token   
                           

class Search:
    def __init__(self, token):
        self.token = token
    # @Returns a JSON object of the artist data
        # id:
        # name:
        # popularity:
        # type:
        # uri:
        # external_urls:
        # followers:
        # genres:
        # href:
        # iamges: 
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

        


