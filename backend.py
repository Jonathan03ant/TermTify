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
                           headers = { 
                                      "Authorization": f"Basic {header}",
                                      "Content-Type": "application/x-www-form-urlencoded"                               
                           },
                           data = {
                               "grant_type": "client_credentials"
                           })
        token = res.json().get("access_token")
        return token   
                           

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
        
    def play_track(self, track_id):
        url = 'https://api.spotify.com/v1/me/player/play'
        header = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {
            "uris": [f"spotify:track:{track_id}"]
        }
        
        try:
            res = requests.put(url, headers=header, json=data)
            if res.status_code == 204:
                print("Track is now playing")
            else:
                print(f"Falied to play track, status code: {res.status_code}")
        except requests.exceptions.RequestException as e:
            print(e)


        


