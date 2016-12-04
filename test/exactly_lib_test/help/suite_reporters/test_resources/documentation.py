from exactly_lib.help.cross_reference_id import CustomCrossReferenceId
from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation


class SuiteReporterDocTestImpl(SuiteReporterDocumentation):
    def __init__(self, singular_name: str):
        super().__init__(singular_name)

    def single_line_description_str(self) -> str:
        return 'single_line_description_str'

    def _see_also_specific(self) -> list:
        return [CustomCrossReferenceId('custom-cross-reference-target')]
