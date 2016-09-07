import praw
from OAuth2Util import OAuth2Util
from reddit_interface.modlog_analyzer import ModlogLogger
import requests.exceptions
from time import sleep

if __name__ == "__main__":
    r = praw.Reddit("windows:ModlogAnalyzer v0.1 by /u/Santi871 - copy modlog to database")
    o = OAuth2Util(r)
    o.refresh(force=True)
    r.config.api_request_delay = 1
    logger = ModlogLogger(r, 'explainlikeimfive')

    while True:
        try:
            logger.pull_modlog()
        except (praw.errors.HTTPException, requests.exceptions.HTTPError):
            sleep(2)

