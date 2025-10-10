from .search_wrapper import Search


class SearchManager:
    def __init__ (self, token):
        self.search_wrapper_api = Search(token)
        self.focus = None
        self.cached_result = {}
        
        
    def run (self, query, search_type="tracks", limit=5, offset=0, market=None):
            return self.search_wrapper_api.search(query, search_type, limit, offset, market)