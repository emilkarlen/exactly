from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR__LONG, \
    OPTION_FOR_PREPROCESSOR
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, Name
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure.structures import text


class _PreprocessorConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('preprocessor', 'preprocessors'))

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'preprocessor_option': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
        })
        return from_simple_description(
            Description(text(_SINGLE_LINE_DESCRIPTION),
                        tp.fnap(_DESCRIPTION_REST)))


PREPROCESSOR_CONCEPT = _PreprocessorConcept()

_SINGLE_LINE_DESCRIPTION = """\
A program that transforms a test case file as the first step in the processing of it."""

_DESCRIPTION_REST = """\
A preprocessor is an executable program, together with optional command line arguments.


When executed, it is given a single (additional) argument: the name of the test case file to preprocess.


It must output the result of the preprocessing on stdout.

An exit code other than 0 indicates error.


A test case is preprocessed only if a preprocessor is given via the {preprocessor_option} option,
or via a test suite.
"""
