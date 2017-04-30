from html.entities import codepoint2name


def convert(s: str) -> str:
    return s.translate(_TRANSLATOR)


class Translator:
    def __getitem__(self, character):
        name = codepoint2name[character]
        return '&' + name + ';'


_TRANSLATOR = Translator()
