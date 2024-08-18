import argparse

from main import get_token, get_artist_JSON, get_artist_id, get_artist_descography

def main():
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
            token = get_token()
            # @Returns a dictionary of the artists discography
            albums = get_artist_descography(token, arguments.artist_name)
            
            for album in albums:
                print(f"Album Namee: {album['name']} | Release Date: {album['release_date']}")
        elif arguments.explanation == "Recently_Played" or arguments.explanation == "rp":
            pass
        else:
            parser.error("Invalid Explanation")
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()