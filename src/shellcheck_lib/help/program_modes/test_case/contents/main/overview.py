from shellcheck_lib.help.program_modes.test_case.contents.main.execution import execution_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.phases import phases_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.help.program_modes.test_case.contents.main.test_case_intro import test_case_intro_documentation
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import para, text

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def overview_documentation(test_case_help: TestCaseHelp) -> doc.SectionContents:
    setup = Setup(test_case_help)
    test_case_intro_contents = test_case_intro_documentation(setup)
    phases_contents = phases_documentation(setup)
    execution_contents = execution_documentation(setup)
    return doc.SectionContents(
        [para(ONE_LINE_DESCRIPTION)],
        [
            doc.Section(text('TEST CASES'),
                        test_case_intro_contents),
            doc.Section(text('PHASES'),
                        phases_contents),
            doc.Section(text('EXECUTION'),
                        execution_contents),
        ])
