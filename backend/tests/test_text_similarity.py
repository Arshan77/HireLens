from app.services.text_similarity import compute_text_similarity


def test_text_similarity_identical():
    text = "We are seeking a Python developer with FastAPI and PostgreSQL experience."
    score, details, warnings = compute_text_similarity(text, text)
    assert score == 100.0
    assert details.similarity_score == 100.0


def test_text_similarity_unrelated():
    resume = "Culinary chef specializing in French pastry, baking, and restaurant management."
    jd = "Python backend engineer building scalable REST APIs and microservices with Kubernetes."
    score, details, warnings = compute_text_similarity(resume, jd)
    assert score < 10.0


def test_text_similarity_overlapping():
    resume = "Software developer proficient in Python, FastAPI, Docker, and PostgreSQL databases."
    jd = "Seeking a Python developer experienced in building web applications with FastAPI and PostgreSQL."
    score, details, warnings = compute_text_similarity(resume, jd)
    assert score > 10.0


def test_text_similarity_empty():
    score, details, warnings = compute_text_similarity("", "Job description text")
    assert score == 0.0
    assert len(warnings) > 0
