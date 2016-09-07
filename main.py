import praw
from OAuth2Util import OAuth2Util
from reddit_interface.modlog_analyzer import ModlogLogger

if __name__ == "__main__":
    r = praw.Reddit("windows:ModlogAnalyzer v0.1 by /u/Santi871 - copy modlog to database")
    o = OAuth2Util(r)
    o.refresh(force=True)
    logger = ModlogLogger(r, 'explainlikeimfive')
    logger.pull_modlog()
