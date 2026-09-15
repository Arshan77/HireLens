from app.services.skill_extractor import extract_skills, extract_skills_with_metadata


def test_extract_skills_exact_matches():
    text = "Proficient in Python, FastAPI, PostgreSQL, and Docker."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills


def test_extract_skills_aliases():
    text = "Built web apps using React.js, Node, Postgres, and Py."
    skills = extract_skills(text)
    assert "React" in skills
    assert "Node.js" in skills
    assert "PostgreSQL" in skills
    assert "Python" in skills


def test_extract_skills_case_insensitivity():
    text = "skills: python, REACT, fastAPI, DOCKER"
    skills = extract_skills(text)
    assert "Python" in skills
    assert "React" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills


def test_extract_skills_deduplication():
    text = "Python, python3, Py, Python Developer, Python API"
    skills = extract_skills(text)
    assert skills.count("Python") == 1


def test_no_false_positive_for_c():
    text = "Strong communication, collaboration, and critical thinking."
    skills = extract_skills(text)
    assert "C" not in skills


def test_no_false_positive_for_go():
    text = "Let's go team! We ongoing cargo operations."
    skills = extract_skills(text)
    assert "Go" not in skills


def test_valid_match_for_isolated_c():
    text = "Core Programming Languages: C, C++, Java, Python."
    skills = extract_skills(text)
    assert "C" in skills
    assert "C++" in skills
    assert "Java" in skills


def test_valid_match_for_go():
    text = "Experienced Backend Engineer skilled in Go, Python, and Redis."
    skills = extract_skills(text)
    assert "Go" in skills
    assert "Python" in skills
    assert "Redis" in skills


def test_extract_skills_with_metadata():
    text = "Experience with Postgres and ReactJS"
    skills, metadata = extract_skills_with_metadata(text)
    assert "PostgreSQL" in skills
    assert "React" in skills
    assert metadata["PostgreSQL"] == "Postgres"
    assert metadata["React"] == "ReactJS"
