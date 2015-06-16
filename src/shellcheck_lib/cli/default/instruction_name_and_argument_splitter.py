import re


class SkipInitialWhiteSpaceAndIdentifyNameByRegEx:
    def __init__(self,
                 reg_ex):
        self._reg_ex = reg_ex

    def __call__(self, line: str):
        match = self._reg_ex.match(line)
        if match is None:
            raise ValueError('Cannot find instruction name')
        return line[:match.end()], line[match.end():]


INSTRUCTION_NAME_REG_EX = re.compile(r"[a-z]+")

splitter = SkipInitialWhiteSpaceAndIdentifyNameByRegEx(INSTRUCTION_NAME_REG_EX)
