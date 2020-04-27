import praw, os, pickle, datetime, re
from praw.models import MoreComments
from Screenshotter import Screenshotter
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from enum import Enum
from urllib.parse import urlparse
from Classifier import classify
from AudioType import AudioType

CLIENT_ID = os.getenv("CLIENT_ID_REDDIT")
CLIENT_SECRET = os.getenv("CLIENT_SECRET_REDDIT")
USER_AGENT = "Autotube"
SCORE_THRESHOLD = 1000
SCORE_COMMENT_RATIO = 0.3
COMMENT_THRESHOLD = 100
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
    for char in text:
        if char not in "/’()*^\\\"<>[]\'~":
            if not (0 <= ord(char) <= 127):  # remove unicode chars
                return True
    return classify(text)


def _clean_str(text):
    text = re.sub("http\S+", lambda match: f" .. {urlparse(match.group()).hostname} link", text)  # replace
    text = re.sub('https*://[\w\.]+\.com[\w/\-]+|https*://[\w\.]+\.com|[\w\.]+\.com/[\w/\-]+',
                  lambda x: " .. {} link".format("re.findall('(?<=\://)[\w\.]+\.com|[\w\.]+\.com', x.group())[0]"),
                  text)  # link with [url].com link
    new_text = []
    char_buffer = []
    for i, char in enumerate(text):
        if len(char_buffer) < 3:
            char_buffer.append(char)
        else:
            char_buffer.pop(0)
            char_buffer.append(char)
            if len(set(char_buffer)) == 1:
                continue
        if char == "\n" or char == "\t":
            new_text.append(".")
        elif char not in "/’()”*^\\\"<>[]\'~":
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


def _remove_parenthesis(string):
    res = ''
    count = 0
    for i in string:
        if i == '(':
            count += 1
        elif i == ')'and count > 0:
            count -= 1
        elif count == 0:
            res += i
    return res


class Subreddit:
    def __init__(self, subreddit):
        self.subreddit = subreddit
        self.sub = reddit.subreddit(subreddit)
        with open("resources/visited.txt", "r") as f:
            self.visited = set([ID.strip() for ID in f.readlines()])

    def get_top(self, n, timefilter):
        timefilter = TimeFilter(timefilter)
        with open("resources/visited.txt", "r") as f:
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
        with open("resources/visited.txt", "r") as f:
            self.visited = set([ID.strip() for ID in f.readlines()])
        if post.id not in self.visited and not post.over_18 and not _check_text(post.title):
            self.sc = Screenshotter(f"https://reddit.com/r/{self.subreddit}/comments/{post.id}/", order.value,
                                    post.id)
            print("Fetching comments...")
            post.comment_sort = order.value
            post.comments.replace_more(limit=72)
            print("Comments fetched!")
            path = self._create_instr(post)
            self.visited.add(post.id)
            with open("resources/visited.txt", "a") as f:
                f.write(f"{post.id}\n")
            return path
        else:
            raise UnsuitableThreadErr(
                "Will not make screenshots. Either thread was already visited or has inappropiate "
                "words in title!")

    def _create_instr(self, post):
        res = [[post.id, _clean_str(f"{post.title} .{post.selftext}")]]
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
        comment_counter = 0
        for comment in comments:
            if comment_counter > 100:
                print("Already saved more than hundred screenshots!... Gonna break outta here")
                break
            if isinstance(comment, MoreComments):
                continue
            if comment.score >= max(25, prevScore * 0.2) and comment.body not in ["[deleted]", "[removed]"] \
                    and not _check_text(comment.body):
                text = _clean_str(comment.body.strip())
                print("NEW_COMMENT" if not prevScore else "SUB_COMMENT", text, comment.id)
                print("Screenshotting comment...")
                try:
                    self.sc.screenshot_comment(comment.id, f"tmp/screenshots/{comment.id}")
                except (NoSuchElementException, TimeoutException):
                    print("Something went wrong! Gonna skip this comment...")
                    continue
                instructions.append([AudioType.TVSOUND if not prevScore else AudioType.SILENCE, ""])
                instructions.append([comment.id, text])
                if lvl > 1: continue # just fetch comments of comments, not comments^3
                print("Expanding comments....")
                self.sc.expand_comment(comment.id)
                comment.replies.replace_more(limit=3)
                print("Comments expanded!")
                self._create_instr_help(comment.replies, comment.score, instructions, lvl + 1)
                self.sc.driver.close()
                self.sc.driver.switch_to.window(self.sc.driver.window_handles[0])
                print("Back on original page")
                comment_counter += 1
