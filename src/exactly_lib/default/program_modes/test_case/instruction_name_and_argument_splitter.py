import re


class SkipInitialWhiteSpaceAndIdentifyNameByRegEx:
    def __init__(self, reg_ex):
        self._reg_ex = reg_ex

    def __call__(self, line: str):
        s = line.lstrip()
        match = self._reg_ex.match(s)
        if match is None:
            raise ValueError('Cannot find instruction name')
        return s[:match.end()], s[match.end():]


INSTRUCTION_NAME_REG_EX = re.compile(r"[_a-zA-Z0-9.-]+")

splitter = SkipInitialWhiteSpaceAndIdentifyNameByRegEx(INSTRUCTION_NAME_REG_EX)
