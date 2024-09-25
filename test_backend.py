from backend import Auth, Player, Search

# Global variable to store the token
token = None

def test_get_token():
    global token  
    
    # Step 1: Initialize the Auth class
    auth = Auth()
    
    # Step 2: Print the authorization URL for the user to log in
    print("Visit this URL to authorize the app:")
    print(auth.get_authorization_url())
    
    # Step 3: After the user authorizes, they must enter the authorization code
    code = input("Enter the authorization code: ")
    
    # Step 4: Exchange the authorization code for an access token
    token = auth.get_token(code)
    
    # Step 5: Print client ID, secret, and token
    if token:
        print(f"Client ID: {auth.client_id}")
        print(f"Client Secret: {auth.client_secret}")
        print(f"Token: {token}")
    else:
        print("Failed to get access token.")

def test_get_devices():
    global token                                                        # Access the global token variable
    # Step 6: Check if the token is available
    if not token:
        print("You need to login and get a token first.")
        return
    
    # Step 7: Initialize Player class with the token
    player = Player(token)

    # Step 8: Get and print available devices
    devices = player.get_devices()  # Remove token argument
    if devices:
        print("Devices:")
        for device in devices:
            print(f"Name: {device['name']}, Type: {device['type']}, Volume: {device['volume_percent']}")
    else:
        print("No devices found or unable to fetch devices.")

def test_get_artist_id():
    global token
    if not token:
        print("You need to login and get a token first.")
        return
    search = Search(token)
    input_artist = input("Enter the artist name: ")
    id = search.get_artist_id(input_artist)
    if id:
        print(f"Artist ID: {id}")
    else:
        print("Failed to get artist ID.")
    
if __name__ == "__main__":
    # Step 10: Test fetching the token and then print devices
    test_get_token()  # This will guide the user through login and token exchange
    print("\n Printing Devices \n")
    test_get_devices()
    test_get_artist_id()
