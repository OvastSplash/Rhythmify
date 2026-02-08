from Main.services.cache import MainCache


class BaseRepository:
    def __init__(self):
        self.cache = MainCache()