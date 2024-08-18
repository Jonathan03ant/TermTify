import requests
from dotenv import load_dotenv
import os
import base64
from requests import post

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    # To get a token, we need to send a POST request to the Spotify API
        # We want to include the following in our request:
            # URL: https://accounts.spotify.com/api/token
            # Headers:
                # Content-Type: application/x-www-form-urlencoded
                # Authorization: Basic <base64 encoded client_id:client_secret>
            # Data:
                # grant_type: client_credentials
 
    url = "https://accounts.spotify.com/api/token"
    header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    response = requests.post(url,
                             headers = {
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Authorization": f"Basic {header}"
                             },
                             data = {
                                    "grant_type": "client_credentials"
                             })
    
    token = response.json().get("access_token")
    return token


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
def get_artist_JSON(token, artist_name):
    url = 'https://api.spotify.com/v1/search'
    header = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 5
    }
    
    res = requests.get(url, headers=header, params=params)
    if res.status_code == 200:
        #print(f"Artist Name: {res.json()['artists']['items'][0]['name']}, Popularity: {res.json()['artists']['items'][0]['popularity']}, Genres: {res.json()['artists']['items'][0]['genres']}")
        return res.json()['artists']['items'] 
    
    
def get_artist_id(token, artist_name):
    artist_data = get_artist_JSON(token, artist_name)
    return artist_data[0]['id']  


# @Returns a dictionary of the artist's discography with each album having 
    # Album Name
    # Release Date ... etc https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
def get_artist_descography(token, artist_name):
    artist_id = get_artist_id(token, artist_name)
    #some kind of error handling here
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "include_groups": "album",
        "limit": 10
    }
    
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        albums = res.json()['items']
        return albums
    else:
        return res.status_code
        
        
# @Returns a dictionary of the artist's top tracks wtth each track having
    #  Track name, Alum they are in, Artist
    #  id, popularity, type, uri, external_urls, href, iamges
    #  ... https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks
def get_artist_top_tracks(token, artist_name):
    artist_id = get_artist_id(token, artist_name)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    header = {
        "Authorization": f"Bearer {token}"
    }
    
    res = requests.get(url, headers=header)
    if res.status_code == 200:
        top_tracks = res.json()['tracks']
        return top_tracks
    else:
        return res.status_code
        


