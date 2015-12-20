from shellcheck_lib.general.textformat.structure import core, paragraph


def text(string: str) -> core.Text:
    return core.Text(string)


def para(texts: iter) -> paragraph.Paragraph:
    return paragraph.Paragraph(texts)


def single_text_para(string: str) -> paragraph.Paragraph:
    return paragraph.Paragraph([text(string)])
