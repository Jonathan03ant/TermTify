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
        return res.json()['artists']['items'] 
    
    
    
    

token = get_token()
artist_data = get_artist_JSON(token, "Kanye West")
id = artist_data[0]['name']
print(id)