from typing import Optional, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.symbol.sdv_structure import references_from_objects_with_symbol_references
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils import file_properties, generic_dependent_value
from exactly_lib.test_case_utils.condition.integer.integer_ddv import IntegerDdv
from exactly_lib.test_case_utils.condition.integer.integer_sdv import IntegerSdv
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils
from exactly_lib.test_case_utils.file_matcher.impl.file_contents_utils import ModelConstructor
from exactly_lib.test_case_utils.files_matcher import models
from exactly_lib.test_case_utils.generic_dependent_value import Sdv, sdv_of_constant_primitive, Ddv, Adv
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, GenericFileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, GenericFilesMatcherSdv
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.functional import map_optional, filter_not_none
from exactly_lib.util.symbol_table import SymbolTable

NAMES = file_contents_utils.NamesSetup(
    file_check_properties.DIR_CONTENTS,
    file_properties.FileType.DIRECTORY,
    syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
)


class _NonRecursiveModelConstructor(file_contents_utils.ModelConstructor[FilesMatcherModel]):

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return models.non_recursive(model.path)


MODEL_CONSTRUCTOR__NON_RECURSIVE = sdv_of_constant_primitive(_NonRecursiveModelConstructor())


def model_constructor__recursive(min_depth: Optional[IntegerSdv],
                                 max_depth: Optional[IntegerSdv]) -> Sdv[ModelConstructor[FilesMatcherModel]]:
    def make_ddv(symbols: SymbolTable) -> Ddv[ModelConstructor[FilesMatcherModel]]:
        def get_int_ddv(x: IntegerSdv) -> IntegerDdv:
            return x.resolve(symbols)

        return _RecursiveModelConstructorDdv(
            map_optional(get_int_ddv, min_depth),
            map_optional(get_int_ddv, max_depth),
        )

    return generic_dependent_value.SdvFromParts(
        make_ddv,
        references_from_objects_with_symbol_references(
            filter_not_none([min_depth, max_depth])
        )
    )


def dir_matches_files_matcher_sdv__generic(
        model_constructor: Sdv[ModelConstructor[FilesMatcherModel]],
        contents_matcher: GenericFilesMatcherSdv,
) -> GenericFileMatcherSdv:
    return file_contents_utils.sdv__generic(
        NAMES,
        model_constructor,
        contents_matcher,
    )


class _RecursiveStructureRenderer(DetailsRenderer):
    def __init__(self,
                 min_depth: Optional[DetailsRenderer],
                 max_depth: Optional[DetailsRenderer],
                 ):
        self._min_depth = min_depth
        self._max_depth = max_depth

    def render(self) -> Sequence[Detail]:
        return self._renderer().render()

    def _renderer(self) -> DetailsRenderer:
        recursive = details.String(
            option_syntax.option_syntax(file_or_dir_contents.RECURSIVE_OPTION.name)
        )
        limits = filter_not_none([
            map_optional(
                lambda d: self._mk_detail(file_or_dir_contents.MIN_DEPTH_OPTION, d),
                self._min_depth
            ),
            map_optional(
                lambda d: self._mk_detail(file_or_dir_contents.MAX_DEPTH_OPTION, d),
                self._max_depth
            ),
        ])

        return details.SequenceRenderer([recursive] + limits)

    @staticmethod
    def _mk_detail(option: a.Option, limit: DetailsRenderer) -> DetailsRenderer:
        return details.HeaderAndValue(
            option_syntax.option_syntax(option.name),
            limit
        )


class _RecursiveModelConstructor(ModelConstructor[FilesMatcherModel]):
    def __init__(self,
                 min_depth: Optional[int],
                 max_depth: Optional[int],
                 ):
        self._min_depth = min_depth
        self._max_depth = max_depth

    @property
    def structure(self) -> DetailsRenderer:
        return _RecursiveStructureRenderer(
            map_optional(details.String, self._min_depth),
            map_optional(details.String, self._max_depth),
        )

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return models.recursive(model.path,
                                self._min_depth,
                                self._max_depth)


class _RecursiveModelConstructorDdv(Ddv[ModelConstructor[FilesMatcherModel]]):
    def __init__(self,
                 min_depth: Optional[IntegerDdv],
                 max_depth: Optional[IntegerDdv],
                 ):
        self._min_depth = min_depth
        self._max_depth = max_depth
        self._validator = ddv_validators.all_of([
            int_ddv.validator()
            for int_ddv in [min_depth, max_depth]
            if int_ddv is not None
        ])

    @property
    def describer(self) -> DetailsRenderer:
        return _RecursiveStructureRenderer(
            map_optional(IntegerDdv.describer, self._min_depth),
            map_optional(IntegerDdv.describer, self._max_depth))

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> Adv[ModelConstructor[FilesMatcherModel]]:
        def get_int_value(x: IntegerDdv) -> int:
            return x.value_of_any_dependency(tcds)

        return generic_dependent_value.ConstantAdv(
            _RecursiveModelConstructor(map_optional(get_int_value, self._min_depth),
                                       map_optional(get_int_value, self._max_depth))
        )
