from typing import List, Dict

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.textformat.textformat_parser import TextParser


class DocumentationElements:
    def __init__(self,
                 format_map: Dict[str, str],
                 src_rel_opt_conf: rel_opts_configuration.RelOptionArgumentConfiguration,
                 src_description: str,
                 dst_rel_opt_conf: rel_opts_configuration.RelOptionArgumentConfiguration,
                 dst_description: str,
                 ):
        self._src_rel_opt_conf = src_rel_opt_conf
        self._src_description = src_description
        self._dst_rel_opt_conf = dst_rel_opt_conf
        self._dst_description = dst_description
        self._tp = TextParser(format_map)

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self._syntax_element_descriptions_for_src() + self._syntax_element_descriptions_for_dst()

    def _syntax_element_descriptions_for_src(self) -> List[SyntaxElementDescription]:
        return [
            rel_opts.path_element(instruction_arguments.SOURCE_PATH_ARGUMENT.name,
                                  self._src_rel_opt_conf.options,
                                  self._tp.fnap(self._src_description))
        ]

    def _syntax_element_descriptions_for_dst(self) -> List[SyntaxElementDescription]:
        return [
            rel_opts.path_element(instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
                                  self._dst_rel_opt_conf.options,
                                  self._tp.fnap(self._dst_description))
        ]

    def see_also_targets(self) -> List[CrossReferenceId]:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT]
        name_and_cross_refs += rel_opts.see_also_name_and_cross_refs(self._dst_rel_opt_conf.options)
        name_and_cross_refs += rel_opts.see_also_name_and_cross_refs(self._src_rel_opt_conf.options)
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)
