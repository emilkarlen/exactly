from typing import List

from exactly_lib.common.help import headers
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_args, \
    cli_argument_syntax_element_description
from exactly_lib.definitions import path
from exactly_lib.definitions import syntax_descriptions, formatting
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.impls import texts
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.path import relative_path_options_documentation as rel_path_doc
from exactly_lib.impls.types.string_source import defs
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

TEXT_UNTIL_END_OF_LINE_ARGUMENT = a.Named('TEXT-UNTIL-END-OF-LINE')


class Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(None, syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT)
        self._tp = TextParser({
            'HERE_DOCUMENT': syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.singular_name,
            'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            'program_type': types.PROGRAM_TYPE_INFO.name,
            'TRANSFORMATION': string_transformer.STRING_TRANSFORMATION_ARGUMENT.name,
            'transformer': syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
            'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
            'SRC_PATH_ARGUMENT': defs.SOURCE_FILE_ARGUMENT_NAME.name,
            'Sym_refs_are_not_substituted': syntax_descriptions.symbols_are_not_substituted_in(
                'the file ' + defs.SOURCE_FILE_ARGUMENT_NAME.name
            ),
            'rel_result_option': formatting.argument_option(path.REL_RESULT_OPTION_NAME),
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'Note': headers.NOTE_LINE_HEADER,
        })

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                                  string_transformer.STRING_TRANSFORMATION_ARGUMENT)

        here_doc_arg = syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.single_mandatory
        string_arg = syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory
        program_token = syntax_elements.PROGRAM_SYNTAX_ELEMENT.single_mandatory
        output_channel_token = a.Choice.of_single_argument_choices(
            a.Multiplicity.MANDATORY,
            [a.Option(option_name)
             for option_name in defs.PROGRAM_OUTPUT_OPTIONS.values()
             ]
        )

        ignore_exit_code_token = a.Single(a.Multiplicity.OPTIONAL,
                                          a.Option(defs.IGNORE_EXIT_CODE))

        file_option = a.Single(a.Multiplicity.MANDATORY,
                               a.Option(defs.FILE_OPTION))

        src_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                defs.SOURCE_FILE_ARGUMENT_NAME)

        return [
            invokation_variant_from_args([string_arg]),
            invokation_variant_from_args([here_doc_arg]),
            invokation_variant_from_args([file_option,
                                          src_file_arg,
                                          optional_transformation_option,
                                          ],
                                         self._tp.fnap(_FILE_DESCRIPTION)),
            invokation_variant_from_args(
                [output_channel_token,
                 ignore_exit_code_token,
                 program_token],
                self._tp.fnap(
                    _PROGRAM_DESCRIPTION) + texts.run_description__with_ignored_exit_code_option__w_str_trans()
            ),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            rel_path_doc.path_element_2(
                defs.src_rel_opt_arg_conf_for_phase(True),
                docs.paras(path_syntax.the_path_of_an_existing_file(FileType.REGULAR, final_dot=True)),
                self._tp.fnap(_RELATIVITIES_BEFORE_ACT)
            ),
            self._transformation_sed(),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT,
                               syntax_elements.STRING_SYNTAX_ELEMENT,
                               syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
                               syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
                               syntax_elements.PROGRAM_SYNTAX_ELEMENT,
                               ]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)

    def _transformation_sed(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            string_transformer.STRING_TRANSFORMATION_ARGUMENT,
            self._tp.fnap(_TRANSFORMATION_DESCRIPTION),
            [
                invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                       string_transformer.TRANSFORMATION_OPTION)]),
            ],
            texts.type_expression_has_syntax_of_primitive([
                syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
            ]),
        )


_TRANSFORMATION_DESCRIPTION = """\
Transforms the original contents.
"""

_PROGRAM_DESCRIPTION = """\
The output from {program_type:a/q}.


{PROGRAM} includes arguments until end of line,
and an optional {TRANSFORMATION} on a following line.
"""

_FILE_DESCRIPTION = """\
The contents of an existing file.


{Sym_refs_are_not_substituted}
"""

_RELATIVITIES_BEFORE_ACT = """\
{Note} {rel_result_option} is only available in phases after {phase[act]:syntax}.
"""