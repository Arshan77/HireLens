from app.services.skill_taxonomy import (
    SKILL_TAXONOMY,
    get_alias_to_canonical_map,
    normalize_skill_name,
)


def test_taxonomy_integrity():
    assert "Python" in SKILL_TAXONOMY
    assert "React" in SKILL_TAXONOMY
    assert "PostgreSQL" in SKILL_TAXONOMY
    assert "FastAPI" in SKILL_TAXONOMY


def test_alias_mapping():
    mapping = get_alias_to_canonical_map()
    assert mapping["postgres"] == "PostgreSQL"
    assert mapping["postgresql"] == "PostgreSQL"
    assert mapping["react.js"] == "React"
    assert mapping["reactjs"] == "React"
    assert mapping["python3"] == "Python"
    assert mapping["py"] == "Python"
    assert mapping["ts"] == "TypeScript"
    assert mapping["js"] == "JavaScript"


def test_normalize_skill_name():
    assert normalize_skill_name("postgres") == "PostgreSQL"
    assert normalize_skill_name("REACTJS") == "React"
    assert normalize_skill_name("fastapi") == "FastAPI"
    assert normalize_skill_name("UnknownSkill") == "Unknownskill"
