from Redditscraper import Subreddit
from TtS import create_video
import os

if __name__ == "__main__":
    #get_top("askreddit", 50, "all")
    #sub = Subreddit("askreddit")
    #sub.get_top(5, "all")
    paths = os.listdir("threads/")
    for path in paths:
        video_path = create_video("threads/" + path, path.split("_")[0])
        #os.system(
        #    f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
        break
        #os.system(f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
