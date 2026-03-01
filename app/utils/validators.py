# app/utils/validators.py
import re

def is_valid_url(url: str) -> bool:
    pattern = r"^(https?:\/\/)?([\w\-]+\.)+[\w]{2,}(\/\S*)?$"
    return re.match(pattern, url) is not None

def is_non_empty_string(s: str) -> bool:
    return bool(s and s.strip())