import re


def uri_pattern_to_uri_rule(rule: str) -> str:
    # TODO properly handle regex patterns
    return re.sub(r'\{([^}]+)\}', r'<\1>', rule)