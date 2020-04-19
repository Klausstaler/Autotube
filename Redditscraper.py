import praw, os, pickle, datetime, re
from praw.models import MoreComments
from Screenshotter import Screenshotter
from enum import Enum

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

class TimeFilter(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"
class SortMethod(Enum):
    NEW = "new"
    BEST = "confidence"
    TOP = "top"
    CONTROVERSIAL = "controversial"
    OLD = "old"
    QA = "qa"

def _check_text(text):
    for word in ["shoot", "shit", "fuck", "nigg", "massacre"]:
        if word in text.lower():
            return False
    return True


def _clean_str(text):
    text = re.sub('https*://[\w\.]+\.com[\w/\-]+|https*://[\w\.]+\.com|[\w\.]+\.com/[\w/\-]+',
                  lambda x: re.findall('(?<=\://)[\w\.]+\.com|[\w\.]+\.com', x.group())[0] + " link", text)
    new_text = []
    for i, char in enumerate(text):
        if char == "\n" or char == "\t":
            new_text.append(".")
        elif char not in ["*", "^", "\\", "\"", "<", ">", "[", "]"]:
            new_text.append(char)
    return "".join(new_text)


class Subreddit:
    def __init__(self, subreddit):
        self.subreddit = subreddit
        self.sub = reddit.subreddit(subreddit)
        with open("visited.txt", "r") as f:
            self.visited = set([ID.strip() for ID in f.readlines()])

    def get_top(self, n, timefilter):
        timefilter = TimeFilter(timefilter)
        with open("visited.txt", "r") as f:
            self.visited = set([ID.strip() for ID in f.readlines()])
        top = self.sub.top(limit=n, time_filter=timefilter.value)
        i = 0
        while i < len(top):
            post = top[i]
            if post.id in self.visited:
                del top[i]
            else:
                i += 1
        return top

    def create_screenshots(self, post, order):
        order = SortMethod(order)
        if post.id not in self.visited and _check_text(post.title):
            self.sc = Screenshotter(f"https://reddit.com/r/{self.subreddit}/comments/{post.id}/?sort={order.value}", post.id)
            print("Fetching comments...")
            post.comments.replace_more(limit=125)
            print("Comments fetched!")
            path = self._create_instr(post)
            self.visited.add(post.id)
            with open("visited.txt", "a") as f:
                f.write(f"{post.id}\n")
            return path

    def _create_instr(self, post):
        res = [[post.id, post.title]]
        self.sc.screenshot_title(f"tmp/screenshots/{post.id}")
        self._create_instr_help(post.comments, 0, res, 1)
        t = datetime.datetime.now()
        path = f"threads/{post}_{t.day}_{t.month}_{t.year}.pkl"
        f = open(path, "wb")
        pickle.dump(res, f)
        f.close()
        return path[8:]

    def _create_instr_help(self, comments, prevScore, instructions, count):
        """
        Creates a list of the different comments, adding special instructions in between.
        """
        for comment in comments:
            if isinstance(comment, MoreComments):
                continue
            if comment.score >= max(20, prevScore * 0.2) and comment.body not in ["[deleted]",
                                                                                  "[removed]"] and _check_text(
                comment.body):
                instructions.append([NEW_COMMENT if not prevScore else SUB_COMMENT, ""])
                text = _clean_str(comment.body.strip())
                instructions.append([comment.id, text])
                print("NEW_COMMENT" if not prevScore else "SUB_COMMENT", text, comment.id)
                self.sc.screenshot_comment(comment.id, f"tmp/screenshots/{comment.id}")
                # self.sc.expand_comment(comment.id)
                # comment.replies.replace_more(10)
                # self._create_instr_help(comment.replies, comment.score, instructions, count+1)
                # self.sc.driver.back()
                # time.sleep(1)

