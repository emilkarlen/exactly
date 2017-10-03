from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.util.cli_syntax.elements import argument as a

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
        from exactly_lib.help_texts.argument_rendering import cl_syntax
        from exactly_lib.help_texts.argument_rendering import path_syntax
        from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts

        relativity_of_expected_arg = a.Named(self._relativity_syntax_element_name)
        optional_relativity_of_expected = a.Single(a.Multiplicity.OPTIONAL,
                                                   relativity_of_expected_arg)
        mandatory_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                              instruction_arguments.PATH_ARGUMENT)
        return ([
                    SyntaxElementDescription(self._path_name,
                                             self._paragraphs(self._path_description_str),
                                             [InvokationVariant(cl_syntax.cl_syntax_for_args(
                                                 [optional_relativity_of_expected,
                                                  mandatory_path]),
                                                 rel_opts.default_relativity_for_rel_opt_type(
                                                     self._path_argument_configuration.argument_syntax_name,
                                                     self._path_argument_configuration.options.default_option)
                                             )]
                                             ),
                ] +
                rel_opts.relativity_syntax_element_descriptions(
                    instruction_arguments.PATH_ARGUMENT,
                    self._path_argument_configuration.options,
                    relativity_of_expected_arg)
                )

    def see_also_items(self) -> list:
        return [CrossReferenceIdSeeAlsoItem(cross_ref)
                for cross_ref in self.see_also_cross_refs()]

    def see_also_cross_refs(self) -> list:
        from exactly_lib.help_texts.entity import syntax_element
        return [syntax_element.HERE_DOCUMENT_SYNTAX_ELEMENT.cross_reference_target]

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)
