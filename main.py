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
    video_setup = VideoSetup(tv_vol_decr=30, music_vol_decr=25, voice_vol=70)
    print("Video setup is set up!")
    top = sub.get_top(200, "all")
    for post in top:
        print(f"Working on {post.title}")
        try:
            path = sub.create_screenshots(post, "top")
        except UnsuitableThreadErr as e:
            continue
        video_path = video_setup.create_video(path, path.split("/")[-1].split("_")[0])
