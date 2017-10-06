from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import path_syntax, cl_syntax
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.cli_syntax.elements import argument as a


class DocumentationElements:
    def __init__(self,
                 format_map: dict,
                 src_rel_opt_conf: rel_opts_configuration.RelOptionArgumentConfiguration,
                 src_description: str,
                 dst_rel_opt_conf: rel_opts_configuration.RelOptionArgumentConfiguration,
                 dst_description: str,
                 ):
        self._src_rel_opt_conf = src_rel_opt_conf
        self._src_description = src_description
        self._dst_rel_opt_conf = dst_rel_opt_conf
        self._dst_description = dst_description
        self._parser = TextParser(format_map)

    def syntax_element_descriptions(self) -> list:
        return self._syntax_element_descriptions_for_src() + self._syntax_element_descriptions_for_dst()

    def _syntax_element_descriptions_for_src(self) -> list:
        mandatory_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                              instruction_arguments.PATH_ARGUMENT)
        relativity_of_arg = a.Named('RELATIVITY-OF-{}-PATH'.format(
            instruction_arguments.SOURCE_PATH_ARGUMENT.name))
        optional_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                       relativity_of_arg)
        file_arg_sed = SyntaxElementDescription(
            instruction_arguments.SOURCE_PATH_ARGUMENT.name,
            self._paragraphs(self._src_description),
            [InvokationVariant(
                self._cl_syntax_for_args(
                    [optional_relativity,
                     mandatory_path]),
                rel_opts.default_relativity_for_rel_opt_type(
                    instruction_arguments.PATH_ARGUMENT.name,
                    self._src_rel_opt_conf.options.default_option))]
        )

        relativity_of_file_seds = rel_opts.relativity_syntax_element_descriptions(
            instruction_arguments.PATH_ARGUMENT,
            self._src_rel_opt_conf.options,
            relativity_of_arg)

        return [file_arg_sed] + relativity_of_file_seds

    def _syntax_element_descriptions_for_dst(self) -> list:
        mandatory_path = path_syntax.path_or_symbol_reference(a.Multiplicity.OPTIONAL,
                                                              instruction_arguments.PATH_ARGUMENT)
        relativity_of_arg = a.Named('RELATIVITY-OF-{}-PATH'.format(
            instruction_arguments.DESTINATION_PATH_ARGUMENT.name))
        optional_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                       relativity_of_arg)
        file_arg_sed = SyntaxElementDescription(
            instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
            self._paragraphs(self._dst_description),
            [InvokationVariant(
                self._cl_syntax_for_args(
                    [optional_relativity,
                     mandatory_path]),
                rel_opts.default_relativity_for_rel_opt_type(
                    instruction_arguments.PATH_ARGUMENT.name,
                    self._dst_rel_opt_conf.options.default_option))]
        )

        relativity_of_file_seds = rel_opts.relativity_syntax_element_descriptions(
            instruction_arguments.PATH_ARGUMENT,
            self._dst_rel_opt_conf.options,
            relativity_of_arg)

        return [file_arg_sed] + relativity_of_file_seds

    def see_also_targets(self) -> list:
        name_and_cross_refs = rel_opts.see_also_name_and_cross_refs(self._dst_rel_opt_conf.options)
        name_and_cross_refs += rel_opts.see_also_name_and_cross_refs(self._src_rel_opt_conf.options)
        from exactly_lib.help_texts.name_and_cross_ref import cross_reference_id_list
        return cross_reference_id_list(name_and_cross_refs)

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(argument_usages)

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        return self._parser.fnap(s, extra)
