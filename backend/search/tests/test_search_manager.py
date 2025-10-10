from backend.Auth import Auth
from backend.search.search_manager import SearchManager

auth = Auth()
global token 




def main():
    if auth.token:
        print("Token is loaded")
        token = auth.token 
    else:
        print(auth.get_authorization_url())
        code = input("Pase auth code here")
        token = auth.get_token(code)
        
        if token:
            print("Token is good")
        else:
            print("Token failed")
            return
    print(f"Token is: {token}")
    
    search_mgr = SearchManager(token)
    
    print("=== Artist search ===")
    res = search_mgr.run("The Weeknd", search_type="artists", limit=3)
    print(res)
    
    print("\n=== Track search ===")
    res = search_mgr.run("blinding lights", search_type="tracks", limit=3)
    print(res)
    
    print("\n=== Album search ===")
    res = search_mgr.run("After Hours", search_type="albums", limit=3)
    
    
    
if __name__ == "__main__":
    main()