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


def playlist_items(plid,next_page_video=None,vidcount=0):
  maxres=2;

  if next_page_video==None:
    pl= youtube.playlistItems().list(
      playlistId=plid,
      part="snippet",
      #maxResults=50
      maxResults=maxres
    ).execute()
  else:
    pl=youtube.playlistItems().list(
      playlistId=plid,
      part="snippet",
      maxResults=maxres,
      pageToken=next_page_video
    ).execute()

  videos=[]

  cur_page_num=pl["pageInfo"]["resultsPerPage"]
  total_num=pl["pageInfo"]["totalResults"]

  if(vidcount+cur_page_num>=total_num):
    for p in pl["items"]:
      videos.append([p["snippet"]["title"],p["snippet"]["resourceId"]["videoId"]]);
    return videos
  else:
    next_page_video=pl["nextPageToken"]
    for p in pl["items"]:
      videos.append([p["snippet"]["title"],p["snippet"]["resourceId"]["videoId"]]);
    videos.extend(playlist_items(plid,next_page_video,vidcount+cur_page_num))
    return videos


pprint(playlist_items("PLD3A38DE4171C4133"))


#next_page_video=pl["nextPageToken"]



# for p in pl["items"]:
#   videos.append([p["snippet"]["title"],p["snippet"]["resourceId"]["videoId"]])


# for i in range(page_total_video//items_per_page_video):
#   pl_next=youtube.playlistItems().list(
#     playlistId="PLD3A38DE4171C4133",
#     part="snippet",
#     maxResults=50,
#     pageToken=next_page_video
#   ).execute()

#   for p in pl_next["items"]:
#     videos.append([p["snippet"]["title"],p["snippet"]["resourceId"]["videoId"]])

#   if "nextPageToken" in pl_next:
#     next_page_video=pl_next["nextPageToken"]

#check it totalreplycount is not zero then go into
#child comments tree for checking

#check for each comment wheter author id == my channel id


#co= youtube.commentThreads().list(
#  videoId="sar-9cxL1wk",
#  part="snippet",
#  maxResults=100
#  ).execute()

#items_per_page_comments=co["pageInfo"]["resultsPerPage"]
#page_total_comments=co["pageInfo"]["totalResults"]

##next_page_comments=co["nextPageToken"]

#comments=[]

##pprint(co)pprint(co)
#for c in co["items"]:
#  if c["id"]==c["snippet"]["topLevelComment"]["id"]:
#    comments.append(c["id"])
#  #comments.append([c["snippet"]["title"],c["snippet"]["resourceId"]["videoId"]])
#pprint(len(comments))

#for i in range(page_total_comments//items_per_page_comments):
#  co_next=youtube.commentThreads().list(
#    videoId=videos[0][1],
#    part="snippet",
#    maxResults=100
#  ).execute()

#  for c in co_next["items"]:
#    comments.append([c["snippet"]["title"],c["snippet"]["resourceId"]["videoId"]])

#  if "nextPageToken" in co_next:
#    next_page_video=co_next["nextPageToken"]
