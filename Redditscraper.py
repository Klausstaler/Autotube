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

class Frame:
    def __init__(self, text, ID, imgpath):
        self.text = text
        self.id = ID
        self.imgpath = imgpath
        self.seq = 0

def get_top(subreddit, n, timefilter):
    if timefilter not in ["day", "week", "month", "year", "all"]:
        raise ValueError("Wrong time filter! Set it to day, week, month, year or \"all\"")
    with open("visited.txt", "r") as f:
        visited = set([ID.strip() for ID in f.readlines()])
        f.close()
    sub = reddit.subreddit(subreddit).top(limit=n, time_filter=timefilter)
    with open("visited.txt", "w") as f:
        for post in sub:
            if post not in visited and check_text(post.title):
                post.comments.replace_more(threshold=2)
                create_instr(post)
                visited.add(post.id)
                f.write(f"{post.id}\n")
                f.flush()


def create_instr(post):
    res = [post.title]
    _create_instr(post.comments, 0, res)
    time = datetime.datetime.now()
    f = open(f"threads/{post}_{time.day}_{time.month}_{time.year}.pkl", "wb")
    pickle.dump(res, f)
    f.close()
    print(res)


def check_text(text):
    for word in ["shoot", "shit", "fuck", "nigg", "massacre"]:
        if word in text.lower():
            return False
    return True



def _create_instr(comments, prevScore, instructions):
    """
    Creates a list of the different comments, adding special instructions in between.
    """
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
    text = re.sub('https*://[\w\.]+\.com[\w/\-]+|https*://[\w\.]+\.com|[\w\.]+\.com/[\w/\-]+',
                lambda x:re.findall('(?<=\://)[\w\.]+\.com|[\w\.]+\.com', x.group())[0] + " link", text)
    new_text = []
    for i, char in enumerate(text):
        if char == "\n" or char == "\t":
            new_text.append(".")
        elif char not in ["*", "^", "\\", "\"", "<", ">"]:
            new_text.append(char)
    return "".join(new_text)
