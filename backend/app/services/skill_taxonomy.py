from typing import Dict, List, Set, Optional

# Master Skill Taxonomy Dictionary
# Maps Canonical Skill Name -> List of Aliases (lowercase for matching)
SKILL_TAXONOMY: Dict[str, List[str]] = {
    # Programming Languages
    "Python": ["python", "python3", "py"],
    "Java": ["java", "jdk", "j2ee"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "C": ["c"],  # Handled with boundary checking
    "C++": ["c++", "cpp", "cplusplus"],
    "C#": ["c#", "csharp", "c-sharp"],
    "Go": ["go", "golang"],
    "Rust": ["rust", "rustlang"],
    "PHP": ["php", "php7", "php8"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift"],

    # Frontend
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular", "angularjs", "angular.js"],
    "Vue": ["vue", "vue.js", "vuejs"],
    "Next.js": ["next.js", "nextjs", "next"],
    "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],

    # Backend
    "Node.js": ["node.js", "nodejs", "node"],
    "Express.js": ["express", "express.js", "expressjs"],
    "FastAPI": ["fastapi", "fast api"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Spring Boot": ["spring boot", "springboot", "spring"],
    "REST API": ["rest api", "restful api", "rest", "restful", "rest apis"],
    "GraphQL": ["graphql"],

    # Databases
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres", "pgsql"],
    "MongoDB": ["mongodb", "mongo"],
    "SQLite": ["sqlite", "sqlite3"],
    "Redis": ["redis"],
    "Oracle": ["oracle", "oracle db"],

    # DevOps / Cloud
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker", "docker container", "dockerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "GCP": ["gcp", "google cloud platform", "google cloud"],
    "CI/CD": ["ci/cd", "ci cd", "cicd", "continuous integration"],

    # Data / AI
    "NumPy": ["numpy"],
    "Pandas": ["pandas"],
    "Matplotlib": ["matplotlib"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "NLP": ["nlp", "natural language processing"],

    # Other Tools & Methodologies
    "Linux": ["linux", "unix", "ubuntu"],
    "Agile": ["agile", "scrum"],
    "Jira": ["jira"],
    "Postman": ["postman"],
}


def get_taxonomy_map() -> Dict[str, List[str]]:
    """Return the raw taxonomy dictionary."""
    return SKILL_TAXONOMY


def get_alias_to_canonical_map() -> Dict[str, str]:
    """
    Build a reverse lookup map from alias -> canonical skill name.
    """
    mapping: Dict[str, str] = {}
    for canonical, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            mapping[alias.lower()] = canonical
    return mapping


def normalize_skill_name(raw_name: str) -> str:
    """
    Normalize raw skill string to canonical skill name if present in taxonomy.
    Otherwise return title-cased string.
    """
    cleaned = raw_name.strip().lower()
    mapping = get_alias_to_canonical_map()
    return mapping.get(cleaned, raw_name.strip().title())


# Canonical Skill Category Mapping
SKILL_CATEGORIES: Dict[str, str] = {
    # Programming Languages
    "Python": "language",
    "Java": "language",
    "JavaScript": "language",
    "TypeScript": "language",
    "C": "language",
    "C++": "language",
    "C#": "language",
    "Go": "language",
    "Rust": "language",
    "PHP": "language",
    "Kotlin": "language",
    "Swift": "language",

    # Frontend
    "HTML": "frontend",
    "CSS": "frontend",
    "React": "frontend",
    "Angular": "frontend",
    "Vue": "frontend",
    "Next.js": "frontend",
    "Tailwind CSS": "frontend",

    # Backend
    "Node.js": "backend",
    "Express.js": "backend",
    "FastAPI": "backend",
    "Flask": "backend",
    "Django": "backend",
    "Spring Boot": "backend",
    "REST API": "backend",
    "GraphQL": "backend",

    # Databases
    "SQL": "database",
    "MySQL": "database",
    "PostgreSQL": "database",
    "MongoDB": "database",
    "SQLite": "database",
    "Redis": "database",
    "Oracle": "database",

    # DevOps / Cloud
    "Git": "devops",
    "GitHub": "devops",
    "Docker": "devops",
    "Kubernetes": "devops",
    "AWS": "devops",
    "Azure": "devops",
    "GCP": "devops",
    "CI/CD": "devops",

    # Data / AI
    "NumPy": "data_ai",
    "Pandas": "data_ai",
    "Matplotlib": "data_ai",
    "scikit-learn": "data_ai",
    "TensorFlow": "data_ai",
    "PyTorch": "data_ai",
    "Machine Learning": "data_ai",
    "Deep Learning": "data_ai",
    "NLP": "data_ai",

    # Other Tools & Methodologies
    "Linux": "tool",
    "Agile": "tool",
    "Jira": "tool",
    "Postman": "tool",
}


def get_skill_category(skill_name: str) -> str:
    """
    Lookup domain category for a skill.
    Normalizes alias to canonical name first.
    Defaults to 'technical' if unknown.
    """
    canonical = normalize_skill_name(skill_name)
    return SKILL_CATEGORIES.get(canonical, "technical")
