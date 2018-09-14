#!/usr/bin/python

# Usage example:
# python comments.py --videoid='<video_id>'

import httplib2
import os
import sys
import nltk
import csv

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    with open("youtube-v3-discoverydocument.json", "r") as f:
        doc = f.read()
        return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

def get_statistics_views(youtube,video_id,token=""):
    response = youtube.videos().list(
    part='statistics, snippet',
    id=video_id).execute()

    view_count = response['items'][0]['statistics']['viewCount']
    like_count = response['items'][0]['statistics']['likeCount']
    dislike_count = response['items'][0]['statistics']['dislikeCount']
    return view_count,like_count,dislike_count

def get_comment_threads(youtube, video_id, comments=[], token=""):
    results = youtube.commentThreads().list(
        part="snippet",
        pageToken=token,
        videoId=video_id,
        textFormat="plainText"
    ).execute()

    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        text = comment["snippet"]["textDisplay"]
        comments.append(text)

    if "nextPageToken" in results:
        return get_comment_threads(youtube, video_id, comments, results["nextPageToken"])
    else:
        return comments

def get_comment_count_threads(youtube, video_id, comments_count=[], token=""):
    results = youtube.commentThreads().list(
        part="snippet",
        pageToken=token,
        videoId=video_id,
        textFormat="plainText"
    ).execute()

    for item in results["items"]:
        comment_count = item["snippet"]["topLevelComment"]
        like_count = comment_count["snippet"]["likeCount"]
        comments_count.append(like_count)

    if "nextPageToken" in results:
        return get_comment_count_threads(youtube, video_id, comments_count, results["nextPageToken"])
    else:
        return comments_count

if __name__ == "__main__":
  argparser.add_argument("--videoid",
    help="Required; ID for video for which the comment will be inserted.")
  args = argparser.parse_args()

  if not args.videoid:
    exit("Please specify videoid using the --videoid= parameter.")

  youtube = get_authenticated_service(args)
  try:
    video_comment_threads = get_comment_threads(youtube, args.videoid)
    video_comment_count_threads = get_comment_count_threads(youtube, args.videoid)
    a,b,c = get_statistics_views(youtube, args.videoid)
    sia = SentimentIntensityAnalyzer()
    with open('compounds.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        #view counts , likes ,dislikes
        writer.writerow([a,b,c])
        for i in range(0,len(video_comment_threads)):
            comment = video_comment_threads[i]
            score = sia.polarity_scores(comment)
            comment_count = video_comment_count_threads[i]
            writer.writerow([comment,score["compound"],comment_count])

    print("Logged sentiments of {0} comments to compounds.csv".format(len(video_comment_threads)))
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
