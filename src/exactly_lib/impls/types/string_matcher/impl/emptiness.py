from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.impls.types.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import details, renderers


class EmptinessStringMatcher(StringMatcherImplBase):
    NAME = file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    @staticmethod
    def new_structure_tree() -> StructureRenderer:
        return renderers.header_only(EmptinessStringMatcher.NAME)

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree()

    def matches_w_trace(self, model: StringSource) -> MatchingResult:
        first_line = self._first_line(model)
        if first_line != '':
            return (
                self._new_tb()
                    .append_details(
                    custom_details.actual(details.String(repr(first_line) + '...'))
                )
                    .build_result(False)
            )
        else:
            return self._new_tb().build_result(True)

    @staticmethod
    def _first_line(file_to_check: StringSource) -> str:
        with file_to_check.contents().as_lines as lines:
            for line in lines:
                return line
        return ''


def sdv() -> StringMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(EmptinessStringMatcher())
