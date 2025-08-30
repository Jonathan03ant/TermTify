from backend.Auth import Auth
from backend.search.search_wrapper import Search

auth = Auth()
global token 

#check if token is there 
#if not, go thru the process

if auth.token:
    print("Token is loaded!")
    token = auth.token 
else:
    print("Going thru token generation setep\n")
    print(auth.get_authorization_url())
    print("Visit the url page above to generate a code\n")
    code = input("Paste auth code here")
    token = auth.get_token(code)
    if token:
        print("Token Generated!")
    else:
        print("Failed to get access token")

print(f"Token is: {token}")     