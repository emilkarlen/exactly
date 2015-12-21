from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.general.textformat.structure.document import SectionContents
from shellcheck_lib.general.textformat.structure.paragraph import Paragraph
from .instruction_description import Description


def render(description: Description) -> SectionContents:
    name_para = _render_name_para(description)
    return SectionContents([name_para], _sections(description))


def _render_name_para(description: Description):
    text_block = Text(description.single_line_description)
    return Paragraph([text_block])


def _sections(description: Description) -> list:
    ret_val = []
    return ret_val
