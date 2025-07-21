from backend import Player, Search

# Import Auth from the backend/Auth.py file
import importlib.util
spec = importlib.util.spec_from_file_location("Auth", "backend/Auth.py")
auth_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth_module)
Auth = auth_module.Auth

# Global variable to store the token
token = None

def test_get_token():
    global token  
    
    # Step 1: Initialize the Auth class
    auth = Auth()

    try:
        # Step 2: Check if a valid token exists
        if not auth.token:
            raise ValueError("No token loaded")
        print("Token is valid, no need for login.")
        token = auth.token
        return  # Skip login if token is valid

    except ValueError:
        # Step 3: If no valid token, request authorization
        print("Visit this URL to authorize the app:")
        print(auth.get_authorization_url())
        
        # Step 4: After the user authorizes, they must enter the authorization code
        code = input("Enter the authorization code: ")
        
        # Step 5: Exchange the authorization code for an access token
        token = auth.get_token(code)
        
        # Step 6: Print client ID, secret, and token
        if token:
            print(f"Client ID: {auth.client_id}")
            print(f"Client Secret: {auth.client_secret}")
            print(f"Token: {token}")
        else:
            print("Failed to get access token.")


def test_get_devices():
    global token                                                        
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
    artist = input("Enter the artist name: ")
    id = search.get_artist_id(artist)
    if id:
        print(f"Artist ID: {id}")
    else:
        print("Failed to get artist ID.")
        
def test_get_artist_metadata():
    global token
    if not token:
        print("You need to login and get a token first.")
        return
    search = Search(token)
    artist = input("Enter the artist name: ")
    metadata = search.get_artist_MetaData(artist)
    if metadata:
        print(f"Artist Metadata: {metadata}")
    else:
        print("Failed to get artist metadata.")
def test_artist_discography():
    global token 
    if not token:
        print("You need to login and get a token first.")
        return
    search = Search(token)
    artist = input("Enter the artist name: ")
    descography = search.get_artist_descography(artist)
    
    if descography:
        print(f"Artist Descography: {descography}")
    else:
        print("Failed to get artist descography.")
        
def test_artist_top_tracks():
    global token
    if not token:
        print("You need to login and get a token first.")
        return
    search = Search(token)
    artist = input("Enter the artist name: ")
    top_tracks = search.get_artist_top_tracks(artist)
    if top_tracks:
        print(f"Artist Top Tracks: {top_tracks}")
    else:
        print("Failed to get artist top tracks.") 
        
def test_get_track_id():
    global token
    if not token:
        print("You need to login and get a token first.")
        return
    search = Search(token)
    artist = input("Enter the artist name: ")
    track = input("Enter the track name: ")
    id = search.get_track_id(artist, track)
    if id:
        print(f"Track ID: {id}")
    else:
        print("Failed to get track ID.")
        
        
if __name__ == "__main__":
    # Step 10: Test fetching the token and then print devices
    test_get_token()  # This will guide the user through login and token exchange
    print("\n Printing Devices \n")
    test_get_devices()
    test_get_artist_id()
    #test_get_artist_metadata()                                     #Working
    #test_artist_discography()                                      #Working
    #test_artist_top_tracks()                                       #Working
    test_get_track_id()                                             #Working