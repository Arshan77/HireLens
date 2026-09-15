import re
from typing import List, Dict, Tuple, Set
from app.services.skill_taxonomy import SKILL_TAXONOMY


def _build_extraction_patterns() -> List[Tuple[str, str, re.Pattern]]:
    """
    Build compiled regex search patterns for each (canonical, alias) pair.
    Sorted by alias length descending so longer/multi-word phrases match first.
    """
    patterns = []
    
    # Collect all (canonical, alias) pairs
    all_pairs = []
    for canonical, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            all_pairs.append((canonical, alias))
            
    # Sort descending by length of alias
    all_pairs.sort(key=lambda x: len(x[1]), reverse=True)

    for canonical, alias in all_pairs:
        escaped_alias = re.escape(alias)
        
        # Special rules for short/ambiguous skills
        if alias.lower() == "c":
            # Must be standalone 'C', not part of C++, C#, or words like 'communication'
            pattern_str = r"(?<![a-zA-Z0-9_#+])C(?![a-zA-Z0-9_#+])"
            compiled = re.compile(pattern_str)  # Case sensitive for standalone 'C'
        elif alias.lower() == "go":
            # Match golang, go language, or standalone capitalized Go/GO or word-bounded 'go' in skill contexts
            pattern_str = r"(?<![a-zA-Z0-9_#+])(?:golang|go\s+language|go\s+developer|go\s+backend|Go|GO)(?![a-zA-Z0-9_#+])"
            compiled = re.compile(pattern_str)
        elif alias.lower() in ("r", "py", "ts", "js"):
            pattern_str = r"(?<![a-zA-Z0-9_#+])" + escaped_alias + r"(?![a-zA-Z0-9_#+])"
            compiled = re.compile(pattern_str, re.IGNORECASE)
        else:
            # Standard word boundary pattern preserving +, #, ., /
            pattern_str = r"(?<![a-zA-Z0-9_#+])" + escaped_alias + r"(?![a-zA-Z0-9_#+])"
            compiled = re.compile(pattern_str, re.IGNORECASE)

        patterns.append((canonical, alias, compiled))

    return patterns


# Cached compiled extraction patterns
COMPILED_PATTERNS = _build_extraction_patterns()


def extract_skills_with_metadata(text: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Extract skills from raw text using boundary-aware regex taxonomy matching.
    
    Returns:
        Tuple[
            sorted_unique_canonical_skills: List[str],
            alias_mapping: Dict[canonical_skill, matched_alias_str]
        ]
    """
    if not text:
        return [], {}

    found_skills: Set[str] = set()
    alias_map: Dict[str, str] = {}

    for canonical, alias, pattern in COMPILED_PATTERNS:
        # Check if pattern matches text
        match = pattern.search(text)
        if match:
            # Special check for 'C' to ensure it wasn't matched inside C++ or C#
            if alias == "c" and ("c++" in text.lower() or "c#" in text.lower()):
                # Only add C if there is an explicit standalone 'C' match not part of C++/C#
                matches = pattern.findall(text)
                # Verify match is not followed by ++ or #
                valid_c = False
                for m in re.finditer(pattern, text):
                    idx = m.end()
                    suffix = text[idx:idx+2]
                    if not (suffix.startswith("++") or suffix.startswith("#")):
                        valid_c = True
                        break
                if not valid_c:
                    continue

            found_skills.add(canonical)
            if canonical not in alias_map:
                alias_map[canonical] = match.group(0)

    sorted_skills = sorted(list(found_skills))
    return sorted_skills, alias_map


def extract_skills(text: str) -> List[str]:
    """
    Extract sorted list of unique canonical skills present in text.
    """
    skills, _ = extract_skills_with_metadata(text)
    return skills
