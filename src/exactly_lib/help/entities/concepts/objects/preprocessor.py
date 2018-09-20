from typing import List

from exactly_lib.cli.definitions.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity.concepts import PREPROCESSOR_CONCEPT_INFO
from exactly_lib.definitions.test_suite import instruction_names, section_infos
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _PreprocessorConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(PREPROCESSOR_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'the_concept': formatting.concept(self.name().singular),
            'preprocessor_option': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
            'is_a_shell_cmd': misc_texts.IS_A_SHELL_CMD,
            'an_exit_code': misc_texts.EXIT_CODE.singular_determined.capitalize(),
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        tp.fnap(_DESCRIPTION_REST)))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.cross_reference_target,
            section_infos.CONFIGURATION.instruction_cross_reference_target(
                instruction_names.INSTRUCTION_NAME__PREPROCESSOR),
            PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_CLI),

        ]


PREPROCESSOR_CONCEPT = _PreprocessorConcept()

_DESCRIPTION_REST = """\
A {the_concept} {is_a_shell_cmd}


When executed, it is given a single (additional) argument: the name of the test case file to transform.


The result of the transformation is the output on stdout.


{an_exit_code} other than 0 indicates error.


A test case file is preprocessed only if a {the_concept} is given via the {preprocessor_option} option,
or via a test suite.
"""
