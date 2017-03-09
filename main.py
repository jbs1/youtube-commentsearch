#!/usr/bin/python

import httplib2
import os
import sys

from pprint import pprint

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secret_870898151800-qihtqcgh0qfqet9kh8h36bop9v92dgcp.apps.googleusercontent.com.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
  message=MISSING_CLIENT_SECRETS_MESSAGE,
  scope=YOUTUBE_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  flags = argparser.parse_args()
  credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
  http=credentials.authorize(httplib2.Http()))



########MY OWN CODE##################

channel= youtube.channels().list(
  mine=True,
  part="id"
  ).execute()
my_channel_id=channel["items"][0]["id"]


def playlist_items(plid,next_page=None,vidcount=0):
  """
  playlist_items gets a playlist id and recusivly assembles a list of of all the videos
  in the list, returning a list with videotitle and ID
  """
  maxres=50;  #more time efficient the more results it can fetch per request
              #210 items => 1->16s | 5->4s | 50->1.3s

  if next_page==None:
    pl= youtube.playlistItems().list(
      playlistId=plid,
      part="snippet",
      maxResults=maxres
    ).execute()
  else:
    pl=youtube.playlistItems().list(
      playlistId=plid,
      part="snippet",
      maxResults=maxres,
      pageToken=next_page
    ).execute()

  videos=[]

  cur_page_num=pl["pageInfo"]["resultsPerPage"]
  if "totalResults" in pl["pageInfo"]:
    total_num=pl["pageInfo"]["totalResults"]
  else:
    total_num=pl["pageInfo"]["resultsPerPage"]

  if(vidcount+cur_page_num>=total_num):
    for p in pl["items"]:
      videos.append([p["snippet"]["title"],p["snippet"]["resourceId"]["videoId"]]);
    return videos
  else:
    next_page=pl["nextPageToken"]
    for p in pl["items"]:
      videos.append([p["snippet"]["title"],p["snippet"]["resourceId"]["videoId"]]);
    videos.extend(playlist_items(plid,next_page,vidcount+cur_page_num))
    return videos



def get_reply_ids(cid,next_page=None,repcount=0):
  """
  fetches recusivly all replies to a comments identified by cid.
  returns list with replyid and  authorname
  """
  maxres=100;  #more time efficient the more results it can fetch per request

  if next_page==None:
    rp= youtube.comments().list(
      parentId=cid,
      part="snippet",
      maxResults=maxres
    ).execute()
  else:
    rp=youtube.comments().list(
      parentId=cid,
      part="snippet",
      maxResults=maxres,
      pageToken=next_page
    ).execute()

  replies=[]
  cur_page_num=rp["pageInfo"]["resultsPerPage"]
  if "totalResults" in rp["pageInfo"]:
    total_num=rp["pageInfo"]["totalResults"]
  else:
    total_num=rp["pageInfo"]["resultsPerPage"]



  if(repcount+cur_page_num>=total_num):
    for r in rp["items"]:
      replies.append([r["id"],r["snippet"]["authorDisplayName"]]);
    return replies
  else:
    next_page=rp["nextPageToken"]
    for r in rp["items"]:
      replies.append([r["id"],r["snippet"]["authorDisplayName"]]);
    replies.extend(playlist_items(cid,next_page,repcount+cur_page_num))
    return replies




def get_comment_ids(vid,next_page=None,comcount=0):
  """
  fetches recusivly all comments for a video identified by cid and their replies using get_reply_ids().
  returns list with commentid and authorname
  """
  maxres=100;  #more time efficient the more results it can fetch per request

  if next_page==None:
    ct= youtube.commentThreads().list(
      videoId=vid,
      part="snippet",
      maxResults=maxres
    ).execute()
  else:
    ct=youtube.commentThreads().list(
      videoId=vid,
      part="snippet",
      maxResults=maxres,
      pageToken=next_page
    ).execute()

  comments=[]

  cur_page_num=ct["pageInfo"]["resultsPerPage"]
  if "totalResults" in ct["pageInfo"]:
    total_num=ct["pageInfo"]["totalResults"]
  else:
    total_num=ct["pageInfo"]["resultsPerPage"]

  if(comcount+cur_page_num>=total_num):
    for c in ct["items"]:
      comments.append([c["snippet"]["topLevelComment"]["id"],c["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]]);
      if(c["snippet"]["totalReplyCount"]!=0):
        comments.extend(get_reply_ids(c["snippet"]["topLevelComment"]["id"]))
    return comments
  else:
    next_page=ct["nextPageToken"]
    for c in ct["items"]:
      comments.append([c["snippet"]["topLevelComment"]["id"],c["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]]);
      if(c["snippet"]["totalReplyCount"]!=0):
        comments.extend(get_reply_ids(c["snippet"]["topLevelComment"]["id"]))
    comments.extend(playlist_items(vid,next_page,comcount+cur_page_num))
    return comments


def get_text_of_comment(cid):
  """
  gets the text for a respective comment id
  """
  ctext=youtube.comments().list(
    id=cid,
    part="snippet",
    textFormat="plainText"
  ).execute()
  return ctext["items"][0]["snippet"]["textDisplay"]


def get_comments_by_user_on_plvids(user,playlistid):
  """
  gets all comments by a specific user on all videos in a specific playlist
  returns a list with video name, video id and comment text
  """
  pli=playlist_items(playlistid)
  out=[]
  for vid in pli:
    for c in get_comment_ids(vid[1]):
      if(user==c[1]):
        out.append([vid[0],vid[1],get_text_of_comment(c[0])])

  return out



#pprint(playlist_items("PLD3A38DE4171C4133"))

pprint(get_comments_by_user_on_plvids("jbs231","PLTo_KBmzxF3sIlOu1Kj1LiF8TXY1o-tv7"))



