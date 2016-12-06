from . import core


class SectionContents(tuple):
    def __new__(cls,
                initial_paragraphs: list,
                sections: list = None):
        """
        :type initial_paragraphs: [core.ParagraphItem]
        :type sections: [Section]
        """
        return tuple.__new__(cls, (initial_paragraphs,
                                   [] if sections is None else sections))

    @property
    def initial_paragraphs(self) -> list:
        """
        :return: [core.ParagraphItem]
        """
        return self[0]

    @property
    def sections(self) -> list:
        """
        :return: [Section]
        """
        return self[1]

    @property
    def is_empty(self) -> bool:
        return not self.initial_paragraphs and not self.sections


def empty_contents() -> SectionContents:
    return SectionContents([], [])


class Section(tuple):
    def __new__(cls,
                header: core.Text,
                contents: SectionContents):
        return tuple.__new__(cls, (header, contents))

    @property
    def header(self) -> core.Text:
        return self[0]

    @property
    def contents(self) -> SectionContents:
        """
        :return: [core.ParagraphItem]
        """
        return self[1]
