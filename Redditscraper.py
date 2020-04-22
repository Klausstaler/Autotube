import praw, os, pickle, datetime, re
from praw.models import MoreComments
from Screenshotter import Screenshotter
from enum import Enum
import time
from Classifier import classify

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
abbrev_dict = {"dm": "direct message", "smh": "shaking my head", "brb": "be right back", "lmk": "let me know",
               "g2g": "got to go", "btw": "by the way", "rt": "retweet", "ama": "ask me anything",
               "tbh": "to be honest",
               "imo": "in my opinion", "imho": "in my humble opinion", "irl": "in real life",
               "afaik": "as far as I know",
               "ack": "acknowledgment", "thx": "thanks", "tba": "to be announced", "wtf": "works for me",
               "tia": "thanks in advance", "nvm": "never mind", "w8": "wait", "wb": "welcome back",
               "faq": "frequently asked questions"}

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


class UnsuitableThreadErr(Exception):
    pass


def _check_text(text):
    for word in ["shoot", "shit", "fuck", "nigg", "massacre"]:
        if word in text.lower():
            return False
    return True


def _clean_str(text):
    text = re.sub('https*://[\w\.]+\.com[\w/\-]+|https*://[\w\.]+\.com|[\w\.]+\.com/[\w/\-]+',
                  lambda x: re.findall('(?<=\://)[\w\.]+\.com|[\w\.]+\.com', x.group())[0] + " link", text)  # replace
    # link with [url].com link
    new_text = []
    for i, char in enumerate(text):
        if char == "\n" or char == "\t":
            new_text.append(".")
        elif char not in ["*", "^", "\\", "\"", "<", ">", "[", "]"]:
            new_text.append(char.lower())
    new_text = "".join(new_text)
    text = []
    for word in new_text.split():  # replaces abbreviations
        stripped_word = word.strip(",.")
        if stripped_word in abbrev_dict:
            new_word = abbrev_dict[stripped_word]
            if stripped_word != word:
                new_word += "."
            text.append(new_word)
        else:
            text.append(word)
    return " ".join(text)


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
        top = [post for post in self.sub.top(limit=n, time_filter=timefilter.value)]
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
        if post.id not in self.visited and not post.over_18 and not classify(post.title):
            self.sc = Screenshotter(f"https://reddit.com/r/{self.subreddit}/comments/{post.id}/", order.value,
                                    post.id)
            print("Fetching comments...")
            post.comment_sort = order.value
            post.comments.replace_more(limit=72)
            print("Comments fetched!")
            path = self._create_instr(post)
            self.visited.add(post.id)
            with open("visited.txt", "a") as f:
                f.write(f"{post.id}\n")
            return path
        else:
            raise UnsuitableThreadErr(
                "Will not make screenshots. Either thread was already visited or has inappropiate "
                "words in title!")

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

    def _create_instr_help(self, comments, prevScore, instructions, lvl):
        """
        Creates a list of the different comments, adding special instructions in between.
        """
        for i,comment in enumerate(comments):
            if isinstance(comment, MoreComments):
                continue
            if comment.score >= max(20, prevScore * 0.2) and comment.body not in ["[deleted]", "[removed]"] \
                    and not classify(comment.body):
                instructions.append([NEW_COMMENT if not prevScore else SUB_COMMENT, ""])
                text = _clean_str(comment.body.strip())
                instructions.append([comment.id, text])
                print("NEW_COMMENT" if not prevScore else "SUB_COMMENT", text, comment.id)
                print("Screenshotting comment...")
                self.sc.screenshot_comment(comment.id, f"tmp/screenshots/{comment.id}")
                if lvl > 1: continue # just fetch comments of comments, not comments^3
                print("Expanding comments....")
                self.sc.expand_comment(comment.id)
                comment.replies.replace_more(limit=3)
                print("Comments expanded!")
                #input()
                self._create_instr_help(comment.replies, comment.score, instructions, lvl + 1)
                self.sc.driver.back()
                time.sleep(2)
                print("Back on original page, clicking on view entire discussion")
                self.sc.driver.find_element_by_xpath("//button[starts-with(text(),'View entire discussion')]").click()
                time.sleep(5 + 0.5*i)
