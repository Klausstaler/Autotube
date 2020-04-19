import praw, os, pickle, datetime, re
from praw.models import MoreComments
from Screenshotter import Screenshotter
import time

CLIENT_ID = os.getenv("CLIENT_ID_REDDIT")
CLIENT_SECRET = os.getenv("CLIENT_SECRET_REDDIT")
USER_AGENT = "Autotube"
SCORE_THRESHOLD = 1000
SCORE_COMMENT_RATIO = 0.3
COMMENT_THRESHOLD = 100
SUB_COMMENT = -2
NEW_COMMENT = -1
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)


class Subreddit:
    def __init__(self, subreddit):
        self.subreddit = subreddit
        self.sub = reddit.subreddit(subreddit)

    def get_top(self, n, timefilter):
        if timefilter not in ["day", "week", "month", "year", "all"]:
            raise ValueError("Wrong time filter! Set it to day, week, month, year or \"all\"")
        with open("visited.txt", "r") as f:
            visited = set([ID.strip() for ID in f.readlines()])
        top = self.sub.top(limit=n, time_filter=timefilter)
        for post in top:
            print("POSTING")
            if post.id not in visited and self._check_text(post.title):
                self.sc = Screenshotter(f"https://reddit.com/r/{self.subreddit}/comments/{post.id}", post.id)
                print("Fetching comments...")
                post.comments.replace_more(limit=125)
                print("Comments fetched!")
                self._create_instr(post)
                visited.add(post.id)
                with open("visited.txt", "w") as f:
                    f.write(f"{post.id}\n")
                    f.close()

    def _check_text(self, text):
        for word in ["shoot", "shit", "fuck", "nigg", "massacre"]:
            if word in text.lower():
                return False
        return True

    def _create_instr(self, post):
        res = [[post.id, post.title]]
        self.sc.screenshot_title(f"images/{post.id}")
        self._create_instr_help(post.comments, 0, res, 1)
        time = datetime.datetime.now()
        f = open(f"threads/{post}_{time.day}_{time.month}_{time.year}.pkl", "wb")
        pickle.dump(res, f)
        f.close()
        # print(res)

    def _create_instr_help(self, comments, prevScore, instructions, count):
        """
        Creates a list of the different comments, adding special instructions in between.
        """
        for comment in comments:
            if isinstance(comment, MoreComments):
                continue
            if comment.score >= max(20, prevScore * 0.2) and comment.body not in ["[deleted]",
                                                                                  "[removed]"] and self._check_text(
                    comment.body):
                instructions.append([NEW_COMMENT if not prevScore else SUB_COMMENT, ""])
                text = self._clean_str(comment.body.strip())
                instructions.append([comment.id, text])
                print("NEW_COMMENT" if not prevScore else "SUB_COMMENT", text, comment.id)
                self.sc.screenshot_comment(comment.id, f"images/{comment.id}")
                # self.sc.expand_comment(comment.id)
                # comment.replies.replace_more(10)
                # self._create_instr_help(comment.replies, comment.score, instructions, count+1)
                # self.sc.driver.back()
                # time.sleep(1)

    def _clean_str(self, text):
        text = re.sub('https*://[\w\.]+\.com[\w/\-]+|https*://[\w\.]+\.com|[\w\.]+\.com/[\w/\-]+',
                      lambda x: re.findall('(?<=\://)[\w\.]+\.com|[\w\.]+\.com', x.group())[0] + " link", text)
        new_text = []
        for i, char in enumerate(text):
            if char == "\n" or char == "\t":
                new_text.append(".")
            elif char not in ["*", "^", "\\", "\"", "<", ">", "[", "]"]:
                new_text.append(char)
        return "".join(new_text)
