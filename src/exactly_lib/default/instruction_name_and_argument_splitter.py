def splitter(line: str) -> str:
    s = line.lstrip()
    if not s:
        raise ValueError('Line contains no instruction name')
    idx = 1
    l = len(s)
    while idx < l and not s[idx].isspace():
        idx += 1
    return s[:idx]
