#!/usr/bin/env python3
import argparse

from backend import Auth, Search

def main():
    
    auth = Auth()
    token = auth.token
    search = Search(token)
    
    parser = argparse.ArgumentParser(
        prog="Tmfy",
        description="Get an artist's discography",
        epilog="source code: git@github.com:Jonathan03ant/TermTify.git")
    
    # Defining the CLI Structure
    # Example: Tmfy search "Ariana Grande" "Albums"
             # Tmfy search "Ariana Grande" "Recently_Played"
               
    parser.add_argument('action', type=str, help="The action to perform: searhc")
    parser.add_argument('artist_name', type=str, help="The name of artist to search for")
    parser.add_argument('explanation', type=str, help="The explanation of the action (Search Artist Albums, Search Artist recently...)")
    

    arguments = parser.parse_args()
    
    if arguments.action == "search" or arguments.action == "sc":
        if arguments.explanation == "Albums" or arguments.explanation == "dsc":
            # @Returns a dictionary of the artists discography
            albums = search.get_artist_descography(arguments.artist_name)
            for album in albums:
                print(f"Album Namee: {album['name']} | Release Date: {album['release_date']}")
                
        elif arguments.explanation == "Recently_Played" or arguments.explanation == "rp":
            pass
        
        elif arguments.explanation == "Top" or arguments.explanation == "tt":
            top_track = search.get_artist_top_tracks(arguments.artist_name)
            for track in top_track:
                print(f"Track Name: {track['name']} | Artist: {track['artists'][0]['name']} | Album: {track['album']['name']} ")
                
        elif arguments.explanation == "latest" or arguments.explanation == "lts":
            pass
        
        else:
            parser.error("Invalid Explanation")
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()