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
        #Empty Query
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty",
                "search_type": search_type,
                "query": query,
                "result": []
            }
        
        #validate search type
        #Empty/wrong search_type
        if not search_type or search_type not in valid_search_types:
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
        type_map = {
            "artists": "artist",
            "tracks": "track",
            "albums": "album",
            "playlists": "playlist",
            "shows": "show",
            "episodes": "episode"
        }
        params["type"] = type_map.get(search_type, search_type)
        
        if market:
            params["market"] = market
        
        """
            This block sends the request, and acquires the response 
            if response.status_code(401, !200) return == generic(false) and empty result
            if not parse the response and return == geric(true) with result list
        """    
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "request.get(search) == 401! \nToken might have expired or is invalid.",
                    "search_type": search_type,
                    "query": query,
                    "result": []
                }
            elif response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Spotify Api Error{response.status_code}",
                    "search_type": search_type,
                    "query": query,
                    "result": []
                }
                   
            # Parse the reponse
            data = response.json()
            if search_type in data:
                raw_data_items = data[search_type]["items"]
                total = data[search_type]["total"]
                
                result = []
                for item in raw_data_items:
                    #1. Build base result_item (universal fields) for all search_types
                    if item is None:
                        continue
                    result_items = {
                        "id": item.get("id"),          # Spotify id for search_type
                        "uri": item.get("uri"),        # Spotify URI, used for playing: spotify:track:uri
                        "name": item.get("name"),
                        "type": item.get("type"),
                        
                        #URLs for Linking
                        "spotify_url": item.get("external_urls", {}).get("spotify"),
                        "preview_url": item.get("preview_url"),
                        "popularity": item.get("popularity"),
                        
                        #rawData if we want the rawdata it self
                        "raw": item
                    }
                    
                    #2. Add search_type specific fields
                    ##searchtype==track
                    if search_type == "tracks":
                        result_items.update({
                            "track_name": item.get("name"),
                            "artists": [
                                {
                                    "name": artists.get("name"),
                                    "id": artists.get("id"),
                                    "uri": artists.get("uri")
                                }
                                for artists in item.get("artists", [])    
                            ],
                            "artist_names": ", ".join([artists.get("name", "") for artists in item.get("artists", [])]),
                            "album": {
                                "name": item.get("album", {}).get("name"),
                                "id": item.get("album", {}).get("id"),
                                "uri": item.get("album", {}).get("uri"),
                                "release_date": item.get("album", {}).get("release_date")
                            },
                            "duration_ms": item.get("duration_ms"), 
                            "explicit": item.get("explicit", True)
                        })
                
                    ##searchtype=albums
                    elif search_type == "albums":
                        result_items.update({
                            "album_name": item.get("name"),
                            "artists": [
                                {
                                    "name": artists.get("name"),
                                    "id": artists.get("id"),
                                    "uri": artists.get("uri")
                                }
                                for artists in item.get("artists", [])
                            ],
                            "artist_names": ", ".join([artists.get("name", "") for artists in item.get("artists", [])]),
                            "release_date": item.get("release_date"),
                            "total_tracks": item.get("total_tracks"),
                            "images": item.get("images", [])
                        })
                        
                    ##searchtype=artists   
                    elif search_type == "artists":
                        result_items.update({
                            "artist_name": item.get("name"),
                            "genres": item.get("genres", []),
                            "followers": item.get("followers", {}).get("total", 0),
                            "images": item.get("images", [])
                        }) 
                                    
                    ##playlists
                    elif search_type == "playlists":
                        result_items.update({
                            "playlist_name": item.get("name"),
                            "owner": item.get("owner", {}).get("display_name"),
                            "owner_id": item.get("owner", {}).get("id"),
                            "track_count": item.get("tracks", {}).get("total", 0),
                            "public": item.get("public", False),
                            "images": item.get("images", [])
                        })
                    
                    ##shows
                    elif search_type == "shows":
                        result_items.update({
                            "show_name": item.get("name"),
                            "publisher": item.get("publisher"),
                            "description": item.get("description"),
                            "languages": item.get("languages", []),
                            "explicit": item.get("explicit", False),
                            "images": item.get("images", [])
                        })
                        
                    ##episodes
                    elif search_type == "episodes":
                        result_items.update({
                            "episode_name": item.get("name"),
                            "description": item.get("description"),
                            "duration_ms": item.get("duration_ms"),
                            "release_date": item.get("release_date"),
                            "explicit": item.get("explicit", False),
                            "images": item.get("images", []),
                            "show": {
                                "name": item.get("show", {}).get("name"),
                                "id": item.get("show", {}).get("id")
                            }
                        })
                    result.append(result_items)
                return {
                    "success": True,
                    "search_type": search_type,
                    "query": query,
                    "total_results": total,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Unexpected response structure for search_type: {search_type}",
                    "search_type": search_type,
                    "query": query,
                    "result": []
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False, 
                "error": f"Network error: {str(e)}", 
                "query": query,
                "search_type": search_type,
                "result": []
            }