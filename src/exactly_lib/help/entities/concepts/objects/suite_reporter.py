from exactly_lib.cli.cli_environment.program_modes.test_suite.command_line_options import OPTION_FOR_REPORTER
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import suite_reporters as reporters
from exactly_lib.help_texts.entity.concepts import SUITE_REPORTER_CONCEPT_INFO
from exactly_lib.help_texts.entity.suite_reporters import all_suite_reporters_cross_refs
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _SuiteReporterConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(SUITE_REPORTER_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'reporter_option': formatting.cli_option(OPTION_FOR_REPORTER),
            'default_reporter': formatting.entity(reporters.DEFAULT_REPORTER.singular_name),
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        tp.fnap(_DESCRIPTION_REST)))

    def see_also_targets(self) -> list:
        return all_suite_reporters_cross_refs()


SUITE_REPORTER_CONCEPT = _SuiteReporterConcept()

_DESCRIPTION_REST = """\
The reporter is specified via the command line using the {reporter_option} option.


Default reporter: {default_reporter}.
"""
