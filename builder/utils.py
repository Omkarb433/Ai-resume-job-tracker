import re
from PyPDF2 import PdfReader

def extract_text(file):
    import PyPDF2
    from docx import Document

    ext = file.name.split('.')[-1].lower()
    if ext == 'pdf':
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text
    elif ext == 'docx':
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return file.read().decode('utf-8')


def parse_resume(text):
    import re
    data = {}

    # smarter name guess
    for line in text.split("\n"):
        if line.strip() and not re.search(r"@|\d", line):
            data["name"] = line.strip()
            break
    else:
        data["name"] = ""

    # email & phone
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    data["email"] = email_match.group(0) if email_match else ""

    phone_match = re.search(r"\+?\d[\d -]{8,}\d", text)
    data["phone"] = phone_match.group(0) if phone_match else ""

    # skills
    skills_keywords = ["Python", "Django", "SQL", "Java", "C++", "JavaScript", "React", "HTML", "CSS"]
    data["skills"] = ", ".join([s for s in skills_keywords if s.lower() in text.lower()])

    return data

