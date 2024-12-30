import re
from bs4 import BeautifulSoup

def clean_text(text):
    """
    Remove unwanted symbols, HTML tags, hashtags, and other extraneous elements from the text.
    """
    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # Remove hashtags
    text = re.sub(r"#\w+", "", text)

    # Remove unwanted symbols
    text = re.sub(r"[^\w\s.,!?-]", "", text)

    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text).strip()

    return text

def format_day_content(content):
    """
    Format the content with proper spacing and structure.
    """
    formatted_sections = []
    current_section = []

    for line in content.split("\n"):
        line = clean_text(line.strip())
        if not line:
            if current_section:
                formatted_sections.append("\n".join(current_section))
                current_section = []
        else:
            current_section.append(line)

    if current_section:
        formatted_sections.append("\n".join(current_section))

    return formatted_sections
