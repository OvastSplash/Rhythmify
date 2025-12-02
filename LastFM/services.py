from pylast import Track, SimilarItem, Tag, LastFMNetwork, Artist, TopItem
from SpotifyController.models import Track as TrackModel, Artist as ArtistModel
from typing import List, Union
from Rhythmify.settings import LAST_FM_KEY, LAST_FM_SECRET
import pylast

class LastFMService:
    @staticmethod
    def get_client() -> LastFMNetwork:
        return pylast.LastFMNetwork(api_key=LAST_FM_KEY, api_secret=LAST_FM_SECRET)

    @staticmethod
    def get_similar_tracks(track: Track, count: int = 10) -> List[SimilarItem]:
        return track.get_similar(count)

    @staticmethod
    def get_tracks_by_genre(genre: Tag, count: int = 5) -> List[Track]:
        return genre.get_top_tracks(count)

    @staticmethod
    def get_similar_artists(artist: Artist, count: int = 5) -> List[SimilarItem]:
        return artist.get_similar(count)

    @staticmethod
    def get_artists_top_tracks(artist: Artist, count: int = 5) -> List[Track]:
        return artist.get_top_tracks(count)

    @staticmethod
    def get_artists_top_genres(artist: Artist, count: int = 5) -> List[TopItem]:
        return artist.get_top_tags(count)


class LastFMClientService:
    def __init__(self):
        self.client = LastFMService.get_client()

    def get_track(self, artist_name: str, track_name: str) -> Track:
        return self.client.get_track(artist_name, track_name)

    def get_genre(self, genre: str) -> Tag:
        return  self.client.get_tag(genre)

    def get_artist(self, artist_name: str) -> Artist:
        return self.client.get_artist(artist_name)


class LastFMDataService:
    def __init__(self):
        self.client = LastFMClientService()
        self.last_fm_service = LastFMService()

    def collect_tracks_by_tracks(self, tracks: List[TrackModel], count: int = 5) -> List[SimilarItem]:
        similar_tracks: List[SimilarItem] = []
        for track in tracks:
            print("Track: ", track.name)
            get_tracks = self.client.get_track(artist_name=track.artists.first().name, track_name=track.name)
            print(get_tracks)
            try:
                similar = self.last_fm_service.get_similar_tracks(track=get_tracks, count=count)

            except Exception as e:
                print(e)
                continue


        return similar_tracks

    def collect_tracks_by_genre(self, genres: List[str], count: int = 5) -> List[Track]:
        tracks: List[Track] = []

        for genre in genres:
            get_genre = self.client.get_genre(genre)
            tracks.extend(self.last_fm_service.get_tracks_by_genre(genre=get_genre, count=count))

        return tracks

    def collect_similar_artists(self, artists: List[ArtistModel], count: int = 5) -> List[SimilarItem]:
        similar_artists: List[SimilarItem] = []

        for artist in artists:
            get_artist = self.client.get_artist(artist.name)
            similar_artists.extend(self.last_fm_service.get_similar_artists(artist=get_artist, count=count))

        return similar_artists

    def collect_artists_top_tracks(self, artists: Union[List[Artist], Artist], count: int = 5) -> List[Track]:
        tracks: List[Track] = []

        if isinstance(artists, list):
            for artist in artists:
                tracks.extend(self.last_fm_service.get_artists_top_tracks(artist=artist, count=count))

        else:
            tracks.extend(self.last_fm_service.get_artists_top_tracks(artist=artists, count=count))

        return tracks

    def transform_similar_artists_to_artists(self, similar_artists: Union[List[SimilarItem], Artist]) -> Union[List[Artist], Artist]:
        if isinstance(similar_artists, list):
            artists: List[Artist] = []

            for artist in similar_artists:
                artists.append(self.client.get_artist(artist.item.name))

            return artists

        else:
            return self.client.get_artist(similar_artists.name)