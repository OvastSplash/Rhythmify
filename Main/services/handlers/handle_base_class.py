from Main.services.cache import MainCache
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService

import logging

from typing import Type
from django.db.models import Model

logger = logging.getLogger(__name__)

class BaseHandler:
    def __init__(self, cache: MainCache | None = None, convert_sp: ConvertSpotifyDataBaseService | None = None):
        self.cache = cache or MainCache()
        self.convert_sp = convert_sp or ConvertSpotifyDataBaseService()