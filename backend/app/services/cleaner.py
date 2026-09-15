import re

def clean_text(raw_text: str) -> str:
    """
    Clean and normalize raw extracted resume text.
    
    Steps:
    1. Normalize special unicode space characters and tabs.
    2. Normalize line endings (\r\n -> \n).
    3. Trim trailing spaces on every line.
    4. Collapse multiple spaces within lines while preserving bullet points & punctuation.
    5. Limit excessive consecutive blank lines (max 2 consecutive newlines).
    6. Strip leading and trailing whitespace.
    """
    if not raw_text:
        return ""

    # 1. Replace non-breaking spaces and zero-width spaces
    text = raw_text.replace("\xa0", " ").replace("\u200b", " ")

    # 2. Normalize carriage returns to standard newline
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Clean line by line
    cleaned_lines = []
    for line in text.split("\n"):
        # Strip outer spaces from each line
        stripped_line = line.strip()
        if stripped_line:
            # Replace 2+ horizontal spaces with 1 space
            stripped_line = re.sub(r"[ \t]+", " ", stripped_line)
            cleaned_lines.append(stripped_line)
        else:
            # Keep blank line representation
            cleaned_lines.append("")

    text = "\n".join(cleaned_lines)

    # 4. Limit consecutive blank lines to max 2 (\n\n)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 5. Final strip
    return text.strip()
