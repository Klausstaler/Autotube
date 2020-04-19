from Redditscraper import Subreddit
from Cutter import VideoSetup
import os

if __name__ == "__main__":
    #get_top("askreddit", 50, "all")
    sub = Subreddit("askreddit")
    video_setup = VideoSetup(20, 25, 70)
    top = sub.get_top(5, "all")
    for post in top:
        path = sub.create_screenshots(post, "top")
        video_path = video_setup.create_video("threads/" + path, path.split("_")[0])
        #os.system(
        #    f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
        break
        #os.system(f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
