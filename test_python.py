from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str

@dataclass
class Track:
    name: str
    genres: list[str]
    rating: float

@dataclass
class UserListenHistory:
    name: str
    tracks: list[Track]
    user: User

@dataclass
class Recommendation:
    tracks: list[Track]
    user: User

class TracksRepository:
    def get_tracks_by_genre(self, genre: str, limit: int = 5) -> list[Track]:
        return Track.object.filter(genres__contains=genre).orger_by('-rating')[:limit]

class AnalythicListenHistoryLoger:
    @staticmethod
    def log(user_listen_history: UserListenHistory):
        print(user_listen_history.tracks)

    @staticmethod
    def get_tracks(tracks: list[Track]):
        print(tracks)

    @staticmethod
    def get_similar_tracks(tracks: list[Track]):
        print(tracks)

class AnalythicListenHistoryProcessor:
    tracks_repository: TracksRepository = TracksRepository()

    def __init__(self, loger: AnalythicListenHistoryLoger) -> None:
        self.loger = loger

    def get_tracks(self, user_listen_history: list[UserListenHistory]) -> list[Track]:
        tracks = list()
        for user_history in user_listen_history:
            tracks.extend(user_history.tracks)

        self.loger.get_tracks(tracks)
        return tracks

    def _search_similar_track(self, track: Track, limit: int = 5) -> list[Track]:
        similar_tracks = set()

        for genre in track.genres:
            similar_tracks.add(self.tracks_repository.get_tracks_by_genre(genre, limit))

        self.loger.get_similar_tracks(similar_tracks)
        return similar_tracks

    def process(self, user_listen_history: list[UserListenHistory]):
        tracks = self.get_tracks(user_listen_history)
        return self._search_similar_track(tracks)


class RecommendationLoger:
    @staticmethod
    def log(recommendation: Recommendation):
        print(recommendation.tracks)

class RecommendationRepository:
    def __init__(self, loger: RecommendationLoger) -> None:
        self.loger = loger

    def save_recommendation(self, tracks: list[Track], user: User):
        self.loger.log(Recommendation(tracks, user))
        return Recommendation(tracks, user)

class GetUser