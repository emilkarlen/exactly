import re


class SkipInitialWhiteSpaceAndIdentifyNameByRegEx:
    def __init__(self,
                 reg_ex):
        self._reg_ex = reg_ex

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


INSTRUCTION_NAME_REG_EX = re.compile(r"")


def splitter(s):
    return s[0], s[1:]
