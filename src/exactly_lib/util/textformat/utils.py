from exactly_lib.util.textformat.structure.document import SectionContents, Section
from exactly_lib.util.textformat.structure.structures import text


def append_section_if_non_empty(output: list,
                                section_title_str_or_text,
                                section_contents: SectionContents):
    if not section_contents.is_empty:
        title = section_title_str_or_text
        if isinstance(title, str):
            title = text(title)
        output.append(Section(title, section_contents))
