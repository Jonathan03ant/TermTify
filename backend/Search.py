import requests, base64, os, secrets, hashlib
from dotenv import load_dotenv
from flask import Flask, redirect, request

class Search:
    def __init__(self, token):
        self.token = token
    
    ###############################################################
    ### PARAMETERS:  artist_name (string)
    ### RETURN:      id
    ### PURPOSE:     Get the artist id from the artist name
    ###############################################################
    def get_artist_id(self, artist_name):
        artist_data = self.get_artist_MetaData(artist_name)
        id = artist_data[0]['id']
        return id
    
    
    ###############################################################
    ### PARAMETERS:  artist_name (string)
    ### RETURN:      list of artist metadata [artists "items" [id, name, ...]]
    ### PURPOSE:     We can refer to this metadata for artist information
    ### Documentation: https://developer.spotify.com/documentation/web-api/reference/search
    ### NOTE:        @param Type = Artist is very important
    ###############################################################
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