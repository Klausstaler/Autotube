import re
import string

re_tok = re.compile(f'([{string.punctuation}“”¨«»®´·º½¾¿¡§£₤‘’])')  # this is a nasty trick I had to pull off. In one


def tokenize(s): return re_tok.sub(r' \1 ', s).split()  # line of the model I defined a custom tokenizer, and Python
# assumes that this one is under __main__, so I have to define it wherever I start the program from....


from Redditscraper import Subreddit, UnsuitableThreadErr
from Cutter import VideoSetup

if __name__ == "__main__":
    sub = Subreddit("askreddit")
    print("Creating video setup...")
    video_setup = VideoSetup(20, 25, 70)
    print("Video setup is set up!")
    top = sub.get_top(5, "all")
    for post in top:
        try:
            path = sub.create_screenshots(post, "top")
        except UnsuitableThreadErr as e:
            continue
        video_path = video_setup.create_video("threads/" + path, path.split("_")[0])
        # os.remove(f"threads/{path}")
        # os.system(
        #    f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
        break
        # os.system(f"python Upload.py --file=\"{video_path}\" --title=\"Test\" --description=\"I am the best\" --keywords=\"Reddit, AskReddit\" --privacyStatus=\"private\"")
