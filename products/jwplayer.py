import urllib.parse
import hashlib
import math
import time
import jwt
from saas_template.settings import (
    JWPLAYER_SECRET
)


def jwt_signed_url(path, host="https://cdn.jwplayer.com"):
    """
    Generate url with signature.
    Args:
      path (str): url path
      host (str): url host
    """

    # Link is valid for 1 hour but normalized to 6 minutes to promote better caching
    exp = math.ceil((time.time() + 3600) / 300) * 300

    params = {}
    params["resource"] = path
    params["exp"] = exp

    # Generate token
    # note that all parameters must be included here
    token = jwt.encode(params, JWPLAYER_SECRET, algorithm="HS256")
    print(token.decode('ascii'))
    url = "{host}{path}?token={token}".format(
        host=host, path=path, token=token.decode('ascii'))

    return url


def get_signed_player(media_id):
    """
    Return signed url for the single line embed javascript.

    Args:
      media_id (str): the media id (also referred to as video key)
      player_id (str): the player id (also referred to as player key)
    """
    path = "/v2/media/{media_id}".format(media_id=media_id)


    # Generate signature
    return jwt_signed_url(path)
