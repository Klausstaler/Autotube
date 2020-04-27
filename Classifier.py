import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import numpy as np
import re, string

re_tok = re.compile(f'([{string.punctuation}“”¨«»®´·º½¾¿¡§£₤‘’])')
def tokenize(s): return re_tok.sub(r' \1 ', s).split()

with open("resources/predict/vectorizer.pkl", "rb") as f:
    _vec = joblib.load(f)

with open("resources/predict/classifier.pkl", "rb") as f:
    _clf = joblib.load(f)


def classify(text, threshold=0.75):
    vectorized = _vec.transform(np.array([text]))
    prob = _clf.predict_proba(vectorized)[:, 1]
    return np.where(prob > threshold, True, False)[0]
