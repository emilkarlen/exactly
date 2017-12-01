from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


def synopsis_section(contents: doc.SectionContents) -> doc.Section:
    return doc.Section(docs.text('SYNOPSIS'), contents)


def description_section(contents: doc.SectionContents) -> doc.Section:
    return doc.Section(docs.text('DESCRIPTION'), contents)


def description_section_if_non_empty(contents: doc.SectionContents) -> list:
    if contents.is_empty:
        return []
    else:
        return [doc.Section(docs.text('DESCRIPTION'), contents)]
