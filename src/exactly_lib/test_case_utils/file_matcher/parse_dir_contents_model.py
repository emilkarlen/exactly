from typing import Optional

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils import generic_dependent_value
from exactly_lib.test_case_utils.condition.integer.integer_ddv import IntegerDdv
from exactly_lib.test_case_utils.condition.integer.integer_sdv import IntegerSdv
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import MandatoryIntegerParser
from exactly_lib.test_case_utils.file_matcher.impl import \
    dir_contents
from exactly_lib.test_case_utils.file_matcher.impl.file_contents_utils import ModelConstructor
from exactly_lib.test_case_utils.files_matcher import models
from exactly_lib.test_case_utils.generic_dependent_value import Sdv, Ddv, Adv, PRIMITIVE
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.util.functional import map_optional, filter_not_none
from exactly_lib.util.symbol_table import SymbolTable


def parse(token_parser: TokenParser
          ) -> Sdv[ModelConstructor[FilesMatcherModel]]:
    return token_parser.consume_and_handle_optional_option(
        dir_contents.MODEL_CONSTRUCTOR__NON_RECURSIVE,
        _parse_recursive_model,
        file_or_dir_contents.RECURSIVE_OPTION.name,
    )


_DEPTH_INTEGER_PARSER = MandatoryIntegerParser(parse_integer_matcher.validator_for_non_negative)


def _parse_recursive_model(token_parser: TokenParser
                           ) -> Sdv[ModelConstructor[FilesMatcherModel]]:
    mb_min_depth = token_parser.consume_and_handle_optional_option3(_DEPTH_INTEGER_PARSER.parse,
                                                                    file_or_dir_contents.MIN_DEPTH_OPTION.name)
    mb_max_depth = token_parser.consume_and_handle_optional_option3(_DEPTH_INTEGER_PARSER.parse,
                                                                    file_or_dir_contents.MAX_DEPTH_OPTION.name)

    def make_ddv(symbols: SymbolTable) -> Ddv[ModelConstructor[FilesMatcherModel]]:
        def get_int_ddv(x: IntegerSdv) -> IntegerDdv:
            return x.resolve(symbols)

        return _ModelConstructorDdv(
            map_optional(get_int_ddv, mb_min_depth),
            map_optional(get_int_ddv, mb_max_depth),
        )

    return generic_dependent_value.SdvFromParts(
        make_ddv,
        references_from_objects_with_symbol_references(
            filter_not_none([mb_min_depth, mb_max_depth])
        )
    )


class _ModelConstructorDdv(Ddv[ModelConstructor[FilesMatcherModel]]):
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
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> Adv[PRIMITIVE]:
        def get_int_value(x: IntegerDdv) -> int:
            return x.value_of_any_dependency(tcds)

        return generic_dependent_value.ConstantAdv(
            _ModelConstructor(map_optional(get_int_value, self._min_depth),
                              map_optional(get_int_value, self._max_depth))
        )


class _ModelConstructor(ModelConstructor[FilesMatcherModel]):
    def __init__(self,
                 min_depth: Optional[int],
                 max_depth: Optional[int],
                 ):
        self._min_depth = min_depth
        self._max_depth = max_depth

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return models.recursive(model.path,
                                self._min_depth,
                                self._max_depth)
