# Automate_sentiment

## setup google cloud
  1. Go to [Google Cloud Console](https://console.cloud.google.com) and create a new project. 
  2. Enable the YouTube Data API v3.
  3. Create credentials (OAuth client ID, Application Type: Other) and download them to `client_secrets.json`.

large part of main.py is the work of [John Fish senticomment](https://github.com/johnafish/senticomment),I added the request for viewcount,dislikecount and likecount, also the likecounts for video.

## running script
`python3 main.py --videoid=Zj8h3ZSc-Aw` , 'Zj8h3ZSc-Aw' is id in this case.

## dataset
after running the py script, you should be able to see your own compound.csv

## running jupyter
final step, now you should be able to see **your own video** stats.
