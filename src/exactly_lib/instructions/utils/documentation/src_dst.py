from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.cross_ref import name_and_cross_ref
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.textformat.textformat_parser import TextParser


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
        return [
            rel_opts.path_element(instruction_arguments.SOURCE_PATH_ARGUMENT.name,
                                  self._src_rel_opt_conf.options,
                                  self._paragraphs(self._src_description))
        ]

    def _syntax_element_descriptions_for_dst(self) -> list:
        return [
            rel_opts.path_element(instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
                                  self._dst_rel_opt_conf.options,
                                  self._paragraphs(self._dst_description))
        ]

    def see_also_targets(self) -> list:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT]
        name_and_cross_refs += rel_opts.see_also_name_and_cross_refs(self._dst_rel_opt_conf.options)
        name_and_cross_refs += rel_opts.see_also_name_and_cross_refs(self._src_rel_opt_conf.options)
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(argument_usages)

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        return self._parser.fnap(s, extra)
