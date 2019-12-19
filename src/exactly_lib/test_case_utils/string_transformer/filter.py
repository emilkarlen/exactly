from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.string_transformer.impl import select
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherAdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerAdv


class SelectStringTransformerAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self, line_matcher: LineMatcherAdv):
        self._line_matcher = line_matcher

    def applier(self, environment: ApplicationEnvironment) -> StringTransformer:
        return select.SelectStringTransformer(self._line_matcher.applier(environment))


class SelectStringTransformerDdv(StringTransformerDdv):
    """
    Keeps lines matched by a given Line Matcher
    and discards lines not matched.
    """

    def __init__(self, line_matcher: LineMatcherDdv):
        self._line_matcher = line_matcher

    def validator(self) -> DdvValidator:
        return self._line_matcher.validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return SelectStringTransformerAdv(self._line_matcher.value_of_any_dependency(tcds))
