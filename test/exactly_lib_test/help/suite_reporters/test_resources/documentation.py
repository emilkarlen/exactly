from exactly_lib.help.cross_reference_id import CustomCrossReferenceId
from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.suite_reporters.names_and_cross_references import suite_reporter_cross_ref
from exactly_lib.help.utils.name_and_cross_ref import SingularNameAndCrossReferenceId


class SuiteReporterDocTestImpl(SuiteReporterDocumentation):
    def __init__(self, singular_name: str,
                 main_description_rest: list = (),
                 syntax_of_output: list = (),
                 exit_code_description: list = ()):
        super().__init__(SingularNameAndCrossReferenceId(singular_name,
                                                         'single line description of suite reporter',
                                                         suite_reporter_cross_ref(singular_name)))
        self._main_description_rest = list(main_description_rest)
        self._syntax_of_output = list(syntax_of_output)
        self._exit_code_description = list(exit_code_description)

    def single_line_description_str(self) -> str:
        return 'single_line_description_str'

    def main_description_rest(self) -> list:
        return self._main_description_rest

    def syntax_of_output(self) -> list:
        return self._syntax_of_output

    def exit_code_description(self) -> list:
        return self._exit_code_description

    def _see_also_specific(self) -> list:
        return [CustomCrossReferenceId('custom-cross-reference-target')]
