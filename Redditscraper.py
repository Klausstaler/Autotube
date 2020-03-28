import praw, os, pickle, datetime, re
from praw.models import MoreComments

CLIENT_ID = os.getenv("CLIENT_ID_REDDIT")
CLIENT_SECRET = os.getenv("CLIENT_SECRET_REDDIT")
USER_AGENT = "Autotube"
SCORE_THRESHOLD = 1000
SCORE_COMMENT_RATIO = 0.3
COMMENT_THRESHOLD = 100
SUB_COMMENT = 2
NEW_COMMENT = 1
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)
visitedThreads = pickle.load(open("visited.pkl","rb"))

def get_top(subreddit, n, timefilter):
    if timefilter not in ["day", "week", "month", "year", "all"]:
        raise ValueError("Wrong time filter! Set it to day, week, month, year or \"all\"")
    with open("visited.pkl", "rb") as f:
        visited = pickle.load(f)
        f.close()
    sub = reddit.subreddit(subreddit).top(limit=n, time_filter=timefilter)
    for post in sub:
        if post not in visited:
            post.comments.replace_more(threshold=2)
            create_instr(post)
            visited.add(post)
    with open("visited.pkl", "wb") as f:
        pickle.dump(f, visited)
        f.close()

def create_instr(post):
    res = [post.title]
    top_score = post.comments[0].score
    _create_instr(post.comments, 0, res)
    time = datetime.datetime.now()
    f = open(f"{post}_{time.day}_{time.month}_{time.year}.pkl", "wb")
    pickle.dump(res, f)
    f.close()
    print(res)


"""
Creates a list of the different comments, adding special instructions in between.
"""
def _create_instr(comments, prevScore, instructions):
    for comment in comments:
        if isinstance(comment, MoreComments):
            continue
        if comment.score >= max(25, prevScore * 0.2) and comment.body not in ["[deleted]", "[removed]"]:
            instructions.append(NEW_COMMENT if not prevScore else SUB_COMMENT)
            text = clean_str(comment.body.strip())
            instructions.append(text)
            comment.replies.replace_more(10)
            _create_instr(comment.replies, comment.score, instructions)


def clean_str(text):
    #new_text = [char for char in text if char not in ["*", "^", "\\", "'", "\""]]
    #"""
    new_text = []
    flag = False
    for i,char in enumerate(text):
        if char == "\n" or char == "\t":
            new_text.append(".")
            flag = False
        elif char not in ["*", "^", "\\", "\""] and not flag:
            new_text.append(char)
    #"""
    return "".join(new_text)


def print_top_comments(comments, nTabs, prevScore):
    for comment in comments:
        if isinstance(comment, MoreComments):
            continue
        if comment.score >= max(10, prevScore * 0.3) and comment.body not in ["[deleted]", "[removed]"]:
            print("  " * nTabs, comment.body, comment.score)
            comment.replies.replace_more(10)
            print_top_comments(comment.replies, nTabs + 1, comment.score)


get_top("askreddit", 1, "all")
