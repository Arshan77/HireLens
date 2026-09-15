import re
from typing import Dict
from app.schemas.resume import SectionData

# Regex patterns for canonical section headers
SECTION_HEADER_PATTERNS = {
    "summary": re.compile(
        r"^(professional\s+summary|executive\s+summary|summary\s+of\s+qualifications|summary|profile|career\s+objective|objective|about\s+me)[:\s]*$",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^(technical\s+skills|skills\s+&\s+technologies|skills\s+and\s+technologies|tech\s+stack|core\s+competencies|key\s+skills|skills|technologies)[:\s]*$",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^(work\s+experience|professional\s+experience|employment\s+history|work\s+history|internship\s+experience|internships|experience)[:\s]*$",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^(academic\s+background|academic\s+qualifications|educational\s+background|education|qualifications)[:\s]*$",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"^(academic\s+projects|personal\s+projects|key\s+projects|software\s+projects|projects)[:\s]*$",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^(licenses\s+&\s+certifications|licenses\s+and\s+certifications|professional\s+certifications|certifications|certificates)[:\s]*$",
        re.IGNORECASE,
    ),
}


def parse_resume_sections(cleaned_text: str) -> SectionData:
    """
    Parse cleaned resume text into structured sections using heuristic header detection.
    
    Sections recognized:
    - contact
    - summary
    - skills
    - experience
    - education
    - projects
    - certifications
    
    Fails gracefully returning empty strings for undetected sections.
    """
    sections_map: Dict[str, list[str]] = {
        "contact": [],
        "summary": [],
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
    }

    if not cleaned_text:
        return SectionData(**{k: "" for k in sections_map})

    lines = cleaned_text.split("\n")
    current_section = "contact"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line matches any section header pattern
        # Lines longer than 60 chars are rarely section headers
        matched_section = None
        if len(stripped) <= 60:
            # Clean punctuation at header ends like 'SKILLS:' -> 'SKILLS'
            clean_header = stripped.rstrip(":-_#")
            for section_name, pattern in SECTION_HEADER_PATTERNS.items():
                if pattern.match(clean_header):
                    matched_section = section_name
                    break

        if matched_section:
            current_section = matched_section
        else:
            sections_map[current_section].append(stripped)

    # Convert list of lines to joined string blocks
    final_sections = {
        key: "\n".join(lines_list).strip()
        for key, lines_list in sections_map.items()
    }

    return SectionData(**final_sections)
