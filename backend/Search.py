import requests


class Search:
    def __init__(self, token):
        self.token = token
        
    """
    Function: universal search api that directly maps to spotify's /search endpoint
    Returns: standardize json format
    Params:
            @query: the search item to search ("name", "song name", "album"....)
            @search_type: what to search for ("artist", "album", "playlist"...)
            @limit: number of results, default at 20
            @offset: pagination, default to 0
    """    
    def search(self, query, search_type, limit=10, offset=0, market=None):
        # Input validation
        valid_search_types = ["artists", "tracks", "albums", "playlists", "shows", "episodes"]
        
        #validate query
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty",
                "search_type": search_type,
                "query": query,
                "result": []
            }
        
        #validate search type
        if search_type not in valid_search_types:
            return {
                "success": False,
                "error": f"Invalid search type. Must be one of: {','.join(valid_search_types)}",
                "search_type": search_type,
                "query": query,
                "result": []
            }
        
        #validate limit (Spotify allows 1-50)
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            return {
                "success": False,
                "error": "Limit must be an integer between 1 and 50",
                "search_type": search_type,
                "query": query,
                "result": []
            }
        
        #valid offset
        if not isinstance(offset, int) or offset < 0:
            return {
                "success": False,
                "error": "Offset must be a non-negative integer",
                "search_type": search_type,
                "query": query,
                "result": []
            }
        
        # Building the request
        url = 'https://api.spotify.com/v1/search'
        headers = {
            "Authorization": f'Bearer {self.token}'
        }
        params = {
            "q": query,
            "type": search_type,
            "limit": limit,
            "offset": offset
        }
        
        if market:
            params["market"] = market
            
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "request.get(search) == 401! \nToken might have expired or is invalid.",
                    "search_type": search_type,
                    "query": query
                }
            elif response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Spotify Api Error{response.status_code}",
                    "search_type": search_type,
                    "query": query
                }
                   
            # Parse the reponse
            data = response.json()
            if search_type in data:
                raw_data_items = data[search_type]["items"]
                total = data[search_type]["total"]
                
                for items in raw_data_items:
                    result_item = {
                        "id": raw_data_items.get["id"],          # Spotify id for search_type
                        "uri": raw_data_items.get["uri"],        # Spotify URI, used for playing: spotify:track:uri
                        "name": raw_data_items.get["name"],
                        "type": raw_data_items.get["type"],
                        
                        #URLs for Linking
                        "spotify_url": raw_data_items.get("external_urls", {}).get("spotify"),
                        "preview_url": raw_data_items.get("preview_url"),
                        
                        #rawData if we want the rawdata it self
                        "raw": raw_data_items
                    }
                
                #Building the result for our return type
    
    ###############################################################
    ### PARAMETERS:  artist_name (string)
    ### RETURN:      id
    ### PURPOSE:     Get the artist id from the artist name
    ### https://developer.spotify.com/documentation/web-api/reference/search
    ###############################################################
    def get_artist_id(self, artist_name):
        artist_data = self.get_artist_MetaData(artist_name)
        id = artist_data[0]['id']
        return id
    
    
    ###############################################################
    ### PARAMETERS:  artist_name (string)
    ### RETURN:      list of artist metadata [artists "items" [id, name, ...]]
    ### PURPOSE:     We can refer to this metadata for artist information
    ### Documentation: https://developer.spotify.com/documentation/web-api/reference/search
    ### NOTE:        @param Type = Artist is very important
    ###############################################################
    def get_artist_MetaData(self, artist_name):
        url = 'https://api.spotify.com/v1/search'
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "q": artist_name,
            "type": "artist",
            "limit": 1
        }
        
        try:
            res = requests.get(url, headers=header, params=params)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        return res.json()['artists']['items']
    
   
    ###############################################################
    ### PARAMETERS:  artist_name (string)
    ### RETURN:      items, [.....,"..", "items(albums)" [name, release_date, ...]]
    ### PURPOSE:     We can refer to this metadata for artist discography
    ### Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
    ### NOTE:        Finds artist id from artist name first
    ###              inserts artist id into the url
    ###############################################################
    def get_artist_descography(self, artist_name):
        artist_id = self.get_artist_id(artist_name)
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "include_groups": "album",
            "limit": 10
        }
        try: 
            res = requests.get(url, headers=header, params=params)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        return res.json()['items']
    
    
    ###############################################################
    ### PARAMETERS:  artist_name (string)
    ### RETURN:      list of artist top tracks [tracks]
    ### PURPOSE:     returns the top tracks of the artist
    ### Documentation: https://developer.spotify.com/documentation/web-api/reference/artists/get-artists-top-tracks/
    ### NOTE:        Finds artist id from artist name first
    ###              inserts artist id into the url
    ###############################################################
    def get_artist_top_tracks(self, artist_name):
        artist_id = self.get_artist_id(artist_name)
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            res = requests.get(url, headers=header)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        return res.json()['tracks']
    
    
    ###############################################################
    ### PARAMETERS:  artist_name (string), track_name (string)
    ### RETURN:      track id
    ### PURPOSE:     Get the track id from the artist name and track name
    ### NOTE:        Finds track metadata from track name and artist name
    ###              @param Type = Track is very important
    ###############################################################
    def get_track_id(self, artist_name, track_name):
        url = 'https://api.spotify.com/v1/search'
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        param = {
            "q": f"track:{track_name} artist:{artist_name}",
            "type": "track",
            "limit": 1
        }
        
        try:
            res = requests.get(url, headers=header, params=param)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        
        tracks = res.json()['tracks']['items']
        if len(tracks) == 0:
            print("Track not found")
            return None
        return tracks[0]['id']

    
    
    ###############################################################
    ### PARAMETERS:  artist_name (string), track_name (string)
    ### RETURN:      returns the first track id from list of tracks
    ### PURPOSE:     Get the track id from the artist name and track name
    ### NOTE:        Strict naming convention
    ###############################################################
    def get_track_id(self, artist_name, track_name):
        url = 'https://api.spotify.com/v1/search'
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        
        param = {
            "q": f"track:{track_name} artist:{artist_name}",
            "type": "track",
            "limit": 3
        }
            
        try:
            res = request.get(url, headers=header, params=param)
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        tracks = res.json()['tracks']['items']
        if len(tracks) == 0:
            print("Track not found")
            return None
        return tracks[0]['id']
        