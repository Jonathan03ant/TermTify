import requests, base64, os, secrets, hashlib
from dotenv import load_dotenv
from flask import Flask, redirect, request

load_dotenv()

app = Flask(__name__)

# The Authorization Code Flow with PKCE 
class Auth:
    
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('redirect_uri')
        self.code_verifier = self.generate_code_verifier() # PKCE Step oen
        self.token = None

    #GENERATE A CODE VERIFIER
    def generate_code_verifier(self):
        return secrets.token_urlsafe(100)
    
    # GENERATE A CODE CHALLENGE
    # Once the code verifier has been generated, we must *HASH* it using the SHA256 algorithm. 
    # This is the value that will be sent within the user authorization request.
    def generate_code_challenge(self):
        return hashlib.sha256(self.code_verifier.encode()).hexdigest()
    
    # GETTING THE AUTHORIZATION URL
    # Endpoint: /authorize, with params including the hashed code challenge
    def get_authorization_url(self):  
        code = self.generate_code_challenge()
        url = 'https://accounts.spotify.com/authorize'
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'code_challenge': code,
            'code_challenge_method': 'S256',
            'scope': 'user-read-playback-state user-modify-playback-state'
        }
        
        request_url = requests.Request('GET', url, params=params).prepare().url
        return request_url

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
        self.token = response_data.get('access_token')
        return self.token
    
    # REFRESHING THE ACCESS TOKEN
    # Endpoint: /api/token
    # Refresh the access token
    def refresh_token(self, refresh_token):
        url = 'https://accounts.spotify.com/api/token'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,   
        }
        
        response = requests.post(url, data=data)
        response_data = response.json()
        self.token = response_data.get('access_token')
        return self.token
    
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
