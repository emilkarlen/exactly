from shellcheck_lib.help.program_modes.test_case.contents.main.introduction import introduction_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.paragraph import para, text

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def overview_documentation(test_case_help: TestCaseHelp) -> doc.SectionContents:
    setup = Setup(test_case_help)
    intro_paragraphs = introduction_documentation(setup)
    return doc.SectionContents([para(ONE_LINE_DESCRIPTION)],
                               [doc.Section(text('INTRODUCTION'),
                                            doc.SectionContents(intro_paragraphs,
                                                                []))])
