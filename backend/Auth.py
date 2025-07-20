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


    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      A 100-character string
    ### PURPOSE:     Generate a code verifier for PKCE
    ###############################################################
    def generate_code_verifier(self):
        return secrets.token_urlsafe(64)
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      A hashed code challenge (string)
    ### PURPOSE:     Generate a code challenge for PKCE, code_verifier --> hashed using SHA256
    #                This is the value that will be sent within the user authorization request. 
    ###############################################################
    def generate_code_challenge(self):
        code_verifier_bytes = self.code_verifier.encode('ascii')
        code_challenge_digest = hashlib.sha256(code_verifier_bytes).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode('ascii').rstrip('=')
        return code_challenge
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### Endpoint:    /authorize
    ### RETURN:      Authorization URL (string)
    ### PURPOSE:     Get the authorization URL for the user to log in with Spotify
    ###############################################################
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
        
        request_url = requests.Request('GET', url, params=params).prepare().url
        return request_url


    ###############################################################
    ### PARAMETERS:  code (string)
    ### Endpoint:    /api/token
    ### RETURN:      access token (string) or None
    ### PURPOSE:     Exchange the authorization code for an access token
    ###############################################################
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
        
        if 'access_token' in response_data and 'refresh_token' in response_data:
            self.token = response_data.get('access_token')
            self.refresh_token = response_data.get('refresh_token')
            self.save_token()
            return self.token
        else:
            print(f"Error retrieving tokens from URL{ response_data }")
            self.token = None
            self.refresh_token = None
            return None

    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      Refreshed access token (string) or None
    ### PURPOSE:     Refresh the access token using the refresh token
    ###############################################################
    def refresh_access_token(self):
        if not self.refresh_token:
            print("No refresh token available on file!")
            return None
        
        url = 'https://accounts.spotify.com/api/token'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,   
        }
        
        response = requests.post(url, data=data)
        response_data = response.json()
        
        if 'access_token' in response_data:
            self.token = response_data.get('access_token')
            self.refresh_token = response_data.get('refresh_token', self.refresh_token)
            self.save_token()
            return self.token 
        else:
            print("Failed to refresh Token")
            return None
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      None
    ### PURPOSE:     Save the access and refresh tokens to a local file
    ###############################################################
    def save_token(self):
        if self.token and self.refresh_token:
            token_data = {
                "access_token": self.token,
                "refresh_token": self.refresh_token
            }
            with open("tokens.json", "w") as file:
                json.dump(token_data, file)
        else:
            print("No token to save.")
         
            
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      True if token is loaded, False if not
    ### PURPOSE:     Load tokens from a file and validate them
    ###############################################################
    def load_token(self):
        try:
            with open("tokens.json", "r") as file:
                token_data = json.load(file)
                self.token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                print("** Login Token Loaded! **\n")
                
                # Check if the token is valid before proceeding 
                #Edge case first, token is loaded and is valid
                if self.token and self.is_token_valid():
                    print("** Access Token is valid **")
                    return True
                
                #Edge Case two: Token is loaded, but is expired
                                # We can use the refresh token
                elif self.token and not self.is_token_valid() and self.refresh_token:
                    print("** Access Token is Expired! **")
                    print("Attempting To Refresh Access Token...")
                    new_token = self.refresh_access_token()
                    
                    if new_token:
                        print("** Token Is Refreshed! **\n")
                        return True
                    else:
                        print("** Refreshing Access Token Failed! **\n")
                        print("Login Required")
                        self.clear_tokens()
                        return False
                else:
                    print("No valid tokens available, login required.")
                    self.clear_tokens()
                    
        except (FileNotFoundError, json.JSONDecodeError):
            # File is missing or empty, prompt login
            print("No valid token file found, user must log in.")
            self.clear_tokens()
            return False
        
        
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      True if token is valid, False if not
    ### PURPOSE:     Verify if the current token is still valid by making a simple API request
    ###############################################################
    def is_token_valid(self):
        url = 'https://api.spotify.com/v1/me/player/devices'
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            print("Access token is expired or invalid")
            return False;
        return response.status_code == 200
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      None
    ### PURPOSE:     Clear tokens from memory when invalid
    ###############################################################
    def clear_tokens(self):
        self.token = None
        self.refresh_token = None
        if os.path.exists("tokens.json"):
            os.remove("tokens.json")
