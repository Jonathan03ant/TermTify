import pytest 
from backend.Auth import Auth
from backend.search.search_wrapper import Search

auth = Auth()
global token 

#check if token is there 
#if not, go thru the process
def generate_token():
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
            return
    print(f"Token is: {token}")   

@pytest.fixture(scope="module")
def search():
    auth = Auth()
    token = getattr(auth, "token", None)
    if not token:
        pytest.skip("No token available from Auth; generate one before running tests")
    return Search(token)


def _assert_base_item_fields(item):
    assert isinstance(item, dict)
    for k in ("id", "uri", "name", "type", "raw"):
        assert k in item

#Q = Song and Search_Type == Track
def test_tracks_search(search):
    print("---------- Test Track Search ----------")
    res = search.search("Lose Yourself Eminem", "tracks", limit=3)
    print(res)
    assert res["success"] is True
    items = res.get("result", [])
    assert isinstance(items, list)
    assert len(items) > 0
    first = items[0]
    _assert_base_item_fields(first)
    assert "track_name" in first
    assert isinstance(first.get("artists", []), list)
    assert "artist_names" in first
    assert "album" in first
    assert "duration_ms" in first
    assert "explicit" in first

#Q = Name and Search_Type == Artist
def test_artists_search(search):
    print("---------- Test Artist Search ----------")
    res = search.search("Eminem", "artists", limit=3)
    assert res["success"] is True
    items = res.get("result", [])
    assert len(items) > 0
    first = items[0]
    _assert_base_item_fields(first)
    assert "artist_name" in first
    assert "genres" in first
    assert "followers" in first

#Q = Album Name and Search_Type == Album
def test_albums_search(search):
    print("---------- Test Album Search ----------")
    res = search.search("The Slim Shady LP", "albums", limit=3)
    assert res["success"] is True
    items = res.get("result", [])
    assert len(items) > 0
    first = items[0]
    _assert_base_item_fields(first)
    assert "album_name" in first
    assert "artist_names" in first
    assert "release_date" in first
    assert "total_tracks" in first


def test_playlists_search(search):
    print("---------- Test Playlist Search ----------")
    res = search.search("2024", "playlists", limit=3)
    assert res["success"] is True
    items = res.get("result", [])
    assert isinstance(items, list)
    if items:
        first = items[0]
        _assert_base_item_fields(first)
        assert "playlist_name" in first
        assert "owner" in first
        assert "track_count" in first


def test_shows_and_episodes_search(search):
    print("---------- Test Shows and Episodes Search ----------")
    show_res = search.search("The Daily", "shows", limit=2)
    assert "success" in show_res
    if show_res.get("success"):
        shows = show_res.get("result", [])
        if shows:
            _assert_base_item_fields(shows[0])
            assert "show_name" in shows[0] or "name" in shows[0]

    ep_res = search.search("The Daily", "episodes", limit=2)
    assert "success" in ep_res
    if ep_res.get("success"):
        eps = ep_res.get("result", [])
        if eps:
            _assert_base_item_fields(eps[0])
            assert "episode_name" in eps[0] or "name" in eps[0]


def test_invalid_search_type(search):
    print("---------- Test Search Invalid Search Type----------")
    res = search.search("test", "invalid_type", limit=1)
    assert res["success"] is False
    assert "Invalid search type" in res.get("error", "")


def test_empty_query(search):
    res = search.search("   ", "tracks")
    assert res["success"] is False
    assert "Query cannot be empty" in res.get("error", "")


def test_limit_offset_validation(search):
    assert search.search("Eminem", "tracks", limit=0)["success"] is False
    assert search.search("Eminem", "tracks", limit=51)["success"] is False
    assert search.search("Eminem", "tracks", offset=-1)["success"] is False
  
