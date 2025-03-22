from ytmusicapi import YTMusic
from typing import List, Dict, Optional
from sptfy import Song
from log import logger


class YTM:
    def __init__(self):
        self.cache: Dict[str, Optional[str]] = {}
        self.yt_music_client = YTMusic()

    def get_youtube_url(self, song: Song) -> Optional[str]:
        if song.spotify_url in self.cache:
            return self.cache[song.spotify_url]

        yt_url = self.search_youtube_music(song.name, song.artists)
        if yt_url is None:
            logger.warning(f"couldn't find song: {song.name} by {', '.join(song.artists)} with a spotify url of '{song.spotify_url}'")

        self.cache[song.spotify_url] = yt_url
        return yt_url

    def search_youtube_music(self, name: str, artists: List[str]) -> Optional[str]:
        # logger.debug(f"looking for youtube url for the song {name}")
        query = f"{name} by {', '.join(artists)}"
        results = self.yt_music_client.search(query, filter="songs", limit=1)

        if len(results) == 0:
            return None

        top_result = results[0]
        # disable this for now because not all spotify titles match youtube titles
        # if "title" not in top_result or top_result["title"].lower() != name.lower():
        #     return None
        if "videoId" not in top_result or top_result["videoId"] is None:
            return None

        return f"https://music.youtube.com/watch?v={top_result["videoId"]}"

    def add_to_cache(self, spotify_url: str, youtube_url: str) -> None:
        self.cache[spotify_url] = youtube_url
