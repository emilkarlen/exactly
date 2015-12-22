from shellcheck_lib.general.textformat.structure import document as doc
from shellcheck_lib.general.textformat.structure.paragraph import para
from shellcheck_lib.test_case.help.instruction_description import Description


def section_contents(name: str, description: Description) -> doc.SectionContents:
    return doc.SectionContents([para('TODO test-case help for instruction ' + name)], [])
