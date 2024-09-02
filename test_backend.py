from backend import Auth, Search, Player 

def test_get_token():
    auth = Auth()
    
    c_id = auth.client_id
    c_sec = auth.client_secret
    token = auth.get_token()
    
    print(f"Client ID: {c_id}")
    print(f"Client Secret: {c_sec}")
    print(f"Token: {token}")
    

if __name__ == "__main__":
    test_get_token()