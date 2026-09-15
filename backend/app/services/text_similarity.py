import re
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.analysis import TextSimilarityDetails
from app.services.cleaner import clean_text

# Conservative technical term preservation mappings (for symbols, delimiters, and multi-word terms)
TECH_TERM_MAP = [
    (r"(?<!\w)c\+\+(?!\w)", "cpp"),
    (r"(?<!\w)c#(?!\w)", "csharp"),
    (r"(?<!\w)\.net(?!\w)", "dotnet"),
    (r"\bnode\.js\b", "nodejs"),
    (r"\bnext\.js\b", "nextjs"),
    (r"\bci[\s/]+cd\b", "cicd"),
    (r"\brest(ful)?\s+apis?\b", "rest_api"),
]

# Exclude programming languages / frameworks from standard stop words
TECH_STOP_WORDS = set(ENGLISH_STOP_WORDS) - {"go", "next"}


def preprocess_for_similarity(text: str) -> str:
    """
    Apply conservative, deterministic preprocessing for text similarity:
    1. Standard whitespace and unicode normalization via clean_text.
    2. Lowercasing.
    3. Technical term preservation for punctuation/delimiter-bearing terms
       (C++, C#, .NET, Node.js, Next.js, CI/CD, REST API).
    """
    if not text:
        return ""
    cleaned = clean_text(text).lower()
    for pattern, repl in TECH_TERM_MAP:
        cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE)
    return cleaned


def compute_text_similarity(
    resume_text: str, job_description_text: str
) -> Tuple[float, TextSimilarityDetails, List[str]]:
    """
    Compute Term Frequency Vector Space Model & Cosine Similarity between
    resume text and job description text.
    
    Uses use_idf=False to avoid the 2-document IDF inversion penalty,
    preserves technical symbols/terms, and evaluates cosine similarity.
    
    Formula:
        cosine(A, B) = (A . B) / (||A|| ||B||)
        score = cosine(A, B) * 100.0
    
    Returns:
        Tuple[
            similarity_score: float (0.0 to 100.0),
            details: TextSimilarityDetails,
            warnings: List[str]
        ]
    """
    warnings: List[str] = []

    if not resume_text or not resume_text.strip():
        warnings.append("Resume text is empty for text similarity computation.")
        details = TextSimilarityDetails(similarity_score=0.0)
        return 0.0, details, warnings

    if not job_description_text or not job_description_text.strip():
        warnings.append("Job description text is empty for text similarity computation.")
        details = TextSimilarityDetails(similarity_score=0.0)
        return 0.0, details, warnings

    r_clean = preprocess_for_similarity(resume_text)
    j_clean = preprocess_for_similarity(job_description_text)

    # Edge case: Identical text
    if r_clean.strip() == j_clean.strip():
        details = TextSimilarityDetails(similarity_score=100.0)
        return 100.0, details, warnings

    try:
        vectorizer = TfidfVectorizer(
            stop_words=list(TECH_STOP_WORDS),
            ngram_range=(1, 1),
            use_idf=False,
            token_pattern=r"(?u)\b[a-zA-Z0-9_]+\b",
        )
        tfidf_matrix = vectorizer.fit_transform([r_clean, j_clean])
        
        sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        raw_similarity = float(sim_matrix[0][0])
        
        # Scale to 0-100 percentage
        score = round(max(0.0, min(100.0, raw_similarity * 100.0)), 1)
    except ValueError as e:
        # Occurs if documents contain only stop words or unparseable tokens
        warnings.append(f"Text similarity calculation fallback: {str(e)}")
        score = 0.0

    details = TextSimilarityDetails(similarity_score=score)
    return score, details, warnings

