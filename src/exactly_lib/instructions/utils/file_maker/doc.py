from typing import List

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_args, \
    cli_argument_syntax_element_description
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.test_case_utils.documentation import relative_path_options_documentation as rel_path_doc, texts
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser
from . import defs


class FileContentsDocumentation:
    def __init__(self,
                 phase_is_after_act: bool,
                 contents_argument_sed: str):
        self._contents_argument_sed = contents_argument_sed
        self._src_rel_opt_arg_conf = defs.src_rel_opt_arg_conf_for_phase(phase_is_after_act)
        self._tp = TextParser({
            'HERE_DOCUMENT': syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.singular_name,
            'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            'program_type': types.PROGRAM_TYPE_INFO.name,
            'TRANSFORMATION': string_transformer.STRING_TRANSFORMATION_ARGUMENT.name,
            'transformer': syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
            'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
            'SRC_PATH_ARGUMENT': defs.SRC_PATH_ARGUMENT.name,
        })

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            self._file_contents_sed(),
            rel_path_doc.path_element_2(self._src_rel_opt_arg_conf,
                                        docs.paras(the_path_of('an existing file.'))),
            self._transformation_sed(),
        ]

    def see_also_targets(self) -> List[CrossReferenceId]:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT,
                               syntax_elements.STRING_SYNTAX_ELEMENT,
                               syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
                               syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
                               syntax_elements.PROGRAM_SYNTAX_ELEMENT,
                               ]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)

    def _file_contents_sed(self) -> SyntaxElementDescription:
        optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                                  string_transformer.STRING_TRANSFORMATION_ARGUMENT)

        here_doc_arg = a.Single(a.Multiplicity.MANDATORY,
                                instruction_arguments.HERE_DOCUMENT)

        string_arg = a.Single(a.Multiplicity.MANDATORY,
                              instruction_arguments.STRING)

        program_token = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument)

        output_channel_token = a.Choice(a.Multiplicity.MANDATORY,
                                        [a.Option(option_name)
                                         for option_name in defs.PROGRAM_OUTPUT_OPTIONS.values()
                                         ]
                                        )

        ignore_exit_code_token = a.Single(a.Multiplicity.OPTIONAL,
                                          a.Option(defs.IGNORE_EXIT_CODE))

        file_option = a.Single(a.Multiplicity.MANDATORY,
                               a.Option(defs.FILE_OPTION))

        src_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                defs.SRC_PATH_ARGUMENT)

        invokation_variants = [
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
                self._tp.fnap(_PROGRAM_DESCRIPTION) + texts.run_with_ignored_exit_code_option__w_str_trans()
            ),
        ]
        return SyntaxElementDescription(self._contents_argument_sed,
                                        [],
                                        invokation_variants)

    def _transformation_sed(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            string_transformer.STRING_TRANSFORMATION_ARGUMENT,
            self._tp.fnap(_TRANSFORMATION_DESCRIPTION),
            [
                invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                       string_transformer.TRANSFORMATION_OPTION)]),
            ]
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


Any {SYMBOL_REFERENCE_SYNTAX_ELEMENT} appearing in the file {SRC_PATH_ARGUMENT} is NOT substituted.
"""
