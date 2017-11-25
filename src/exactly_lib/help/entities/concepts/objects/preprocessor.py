from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity.concepts import PREPROCESSOR_CONCEPT_INFO
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _PreprocessorConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(PREPROCESSOR_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'preprocessor_option': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        tp.fnap(_DESCRIPTION_REST)))


PREPROCESSOR_CONCEPT = _PreprocessorConcept()

_DESCRIPTION_REST = """\
A preprocessor is an executable program, together with optional command line arguments.


When executed, it is given a single (additional) argument: the name of the test case file to preprocess.


It must output the result of the preprocessing on stdout.

An exit code other than 0 indicates error.


A test case is preprocessed only if a preprocessor is given via the {preprocessor_option} option,
or via a test suite.
"""
