import re
from collections import Counter

COMMON_STOP = set("""
a the an and or for to of in on with by from into at as is are was were be being been it its that this those these your you we our their they he she his her
""".split())

def tokenize(text: str):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in COMMON_STOP]

def ats_score(resume_text: str, jd_text: str) -> float:
    """Simple keyword overlap score (0-100)."""
    r, j = set(tokenize(resume_text)), set(tokenize(jd_text))
    if not j:
        return 0.0
    overlap = len(r & j) / len(j)
    return round(overlap * 100, 2)
