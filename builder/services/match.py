from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_vectorizer = TfidfVectorizer(max_features=4000, ngram_range=(1,2))

def match_score(resume_text: str, jd_text: str) -> float:
    docs = [resume_text or "", jd_text or ""]
    tfidf = _vectorizer.fit_transform(docs)
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(sim) * 100, 2)
