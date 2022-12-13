import re

def extract_flag(inp):
    return re.findall(r'CYBERLEAGUE{.+?}', inp)
