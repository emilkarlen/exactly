from shellcheck_lib.help.program_modes.test_case.contents.main.intro_environment import execution_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.intro_phases import phases_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.intro_test_case import test_case_intro_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.ref_test_case_files import test_case_files_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.ref_test_case_processing import \
    test_case_processing_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.test_outcome import test_outcome_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.utils import Setup, TestCaseHelpRendererBase
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import para, text

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


class OverviewRenderer(TestCaseHelpRendererBase):
    def apply(self) -> doc.SectionContents:
        setup = Setup(self.test_case_help)
        test_case_intro_contents = test_case_intro_documentation(setup)
        phases_contents = phases_documentation(setup)
        execution_contents = execution_documentation(setup)
        return doc.SectionContents(
            [para(ONE_LINE_DESCRIPTION)],
            [
                doc.Section(text('OVERVIEW'),
                            doc.SectionContents(
                                [],
                                [
                                    doc.Section(text('Test cases'),
                                                test_case_intro_contents),
                                    doc.Section(text('Environment'),
                                                execution_contents),
                                    doc.Section(text('Phases'),
                                                phases_contents),
                                ])),
                doc.Section(text('TEST CASE FILES'),
                            test_case_files_documentation(setup)),
                doc.Section(text('TEST CASE PROCESSING'),
                            test_case_processing_documentation(setup)),
                doc.Section(text('TEST OUTCOME'),
                            test_outcome_documentation(setup)),
            ])
