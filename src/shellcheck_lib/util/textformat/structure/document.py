from . import core


class SectionContents(tuple):
    def __new__(cls,
                initial_paragraphs: list,
                sections: list):
        """
        :type initial_paragraphs: [core.ParagraphItem]
        :type sections: [Section]
        """
        return tuple.__new__(cls, (initial_paragraphs, sections))

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
