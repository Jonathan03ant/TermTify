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
        self.load_token()
        self.token = None    #output
        self.refresh_token = None    #output


    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      A 100-character string
    ### PURPOSE:     Generate a code verifier for PKCE
    ###############################################################
    def generate_code_verifier(self):
        return secrets.token_urlsafe(100)
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      A hashed code challenge (string)
    ### PURPOSE:     Generate a code challenge for PKCE, hashed using SHA256
    ###############################################################
    def generate_code_challenge(self):
        return hashlib.sha256(self.code_verifier.encode()).hexdigest()
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      Authorization URL (string)
    ### PURPOSE:     Get the authorization URL for the user to log in with Spotify
    ###############################################################
    def get_authorization_code(self):  
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


    ###############################################################
    ### PARAMETERS:  code (string)
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
        #print(f"Response From get_token: {response_data}")
        
        if 'access_token' in response_data and 'refresh_token' in response_data:
            self.token = response_data.get('access_token')
            self.refresh_token = response_data.get('refresh_token')
            self.save_token() 
        else:
            print(f"Error retriving tokens{ response_data }")
            self.token = None
            self.refresh_token = None
        return self.token
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      Refreshed access token (string) or None
    ### PURPOSE:     Refresh the access token using the refresh token
    ###############################################################
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
            self.save_token
            return self.token 
        else:
            print("Failed to refresh Token")
            return None
    
    
    ###############################################################
    ### PARAMETERS:  None
    ### RETURN:      None
    ### PURPOSE:     Save the access and refresh tokens to a file
    ###############################################################
    def save_token(self):
        if self.token and self.refresh_token:
            token_data = {
                "access_token": self.token,
                "refresh_token": self.refresh_token
            }
            with open("token.json", "w") as file:
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
            with open("token.json", "r") as file:
                token_data = json.load(file)
                self.token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                print("Login Token Loaded\n")
                
                # Check if the token is valid before proceeding 
                if not self.token or not self.refresh_token:
                    print("Invalid token data, prompting login.")
                    self.token = None
                    self.refresh_token = None
                else:
                    print("Tokens are valid")
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            # File is missing or empty, prompt login
            print("No valid token file found, user must log in.")
            self.token = None
            self.refresh_token = None
            return False
    
auth = Auth()

@app.route('/login')
def login():
    return redirect(auth.get_authorization_url()) #sends the rpepared URL to the user

@app.route('/callback')
def callback():
    code = request.args.get('code')  
    if not code:
        return "Authorization failed", 
    
    token = auth.get_token(code)  
    
    if token:
        return f"Access Token: {token}"  
    else:
        return "Failed to get access token", 
    
    
if __name__ == "__main__":
    app.run(debug=True)
