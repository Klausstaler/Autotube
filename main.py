from Redditscraper import Subreddit, UnsuitableThreadErr
from Cutter import VideoSetup
import os

if __name__ == "__main__":
    #get_top("askreddit", 50, "all")
    sub = Subreddit("askreddit")
    print("Creating video setup...")
    video_setup = VideoSetup(20, 25, 70)
    print("Video setup is set up!")
    top = sub.get_top(5, "all")
    print(top)
    for post in top:
        try:
            path = sub.create_screenshots(post, "top")
        except UnsuitableThreadErr as e:
            continue
        video_path = video_setup.create_video("threads/" + path, path.split("_")[0])
        #os.remove(f"threads/{path}")
        #os.system(
        #    f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
        break
        #os.system(f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
