from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT
from exactly_lib.instructions.utils.documentation.relative_path_options_documentation import path_elements
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

EMPTY_ARGUMENT_CONSTANT = a.Constant(EMPTY_ARGUMENT)


class StringOrHereDocOrFile:
    def __init__(self,
                 path_name: str,
                 relativity_syntax_element_name: str,
                 path_argument_configuration: RelOptionArgumentConfiguration,
                 path_description_str: str):
        self._path_name = path_name
        self._relativity_syntax_element_name = relativity_syntax_element_name
        self._path_argument_configuration = path_argument_configuration
        self._expected_file_arg = a.Option(parse_here_doc_or_file_ref.FILE_ARGUMENT_OPTION,
                                           path_name)
        self._path_description_str = path_description_str

        format_map = {
            'expected_file_arg': path_name,
        }
        self._parser = TextParser(format_map)

    def argument_usage(self, multiplicity: a.Multiplicity) -> a.ArgumentUsage:
        return a.Choice(multiplicity,
                        [instruction_arguments.STRING,
                         instruction_arguments.HERE_DOCUMENT,
                         self._expected_file_arg])

    def syntax_element_descriptions(self) -> list:
        return path_elements(
            self._path_name,
            self._path_argument_configuration.options,
            self._paragraphs(self._path_description_str)
        )

    def see_also_targets(self) -> list:
        return cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
            syntax_elements.STRING_SYNTAX_ELEMENT,
        ])

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)
