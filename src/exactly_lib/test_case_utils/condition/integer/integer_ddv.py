from typing import Callable, Optional, Set

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.condition.comparison_structures import OperandDdv
from exactly_lib.test_case_utils.condition.integer.evaluate_integer import python_evaluate, NotAnIntegerException
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render import strings

CustomIntegerValidator = Callable[[int], Optional[TextRenderer]]


class IntegerDdv(OperandDdv[int]):
    def __init__(self,
                 int_expression: StringDdv,
                 custom_integer_validator: Optional[CustomIntegerValidator] = None):
        self._describer = details.String(strings.AsToStringObject(int_expression.describer()))
        self._primitive_value_computer = _PrimitiveValueComputer(int_expression)
        self._validator = _IntegerDdvValidator(self._primitive_value_computer,
                                               custom_integer_validator)

    def describer(self) -> DetailsRenderer:
        return self._describer

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._primitive_value_computer.resolving_dependencies()

    def validator(self) -> DdvValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> int:
        return self._primitive_value_computer.value_when_no_dir_dependencies()

    def value_of_any_dependency(self, tcds: Tcds) -> int:
        return self._primitive_value_computer.value_of_any_dependency(tcds)


class _PrimitiveValueComputer:
    """Computes the primitive value"""

    def __init__(self, int_expression: StringDdv):
        self._int_expression = int_expression
        self._primitive_value = None

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._int_expression.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> int:
        if self._primitive_value is None:
            self._get_primitive_value(self._int_expression.value_when_no_dir_dependencies())

        return self._primitive_value

    def value_of_any_dependency(self, tcds: Tcds) -> int:
        if self._primitive_value is None:
            self._get_primitive_value(self._int_expression.value_of_any_dependency(tcds))

        return self._primitive_value

    def _get_primitive_value(self, int_expr: str):
        try:
            self._primitive_value = python_evaluate(int_expr)
        except NotAnIntegerException as ex:
            msg = 'Not an integer expression: `{}\''.format(ex.value_string)
            raise NotAnIntegerException(msg)


class _IntegerDdvValidator(DdvValidator):
    def __init__(self,
                 value_computer: _PrimitiveValueComputer,
                 custom_validator: Optional[CustomIntegerValidator]):
        self._value_computer = value_computer
        self._custom_validator = (custom_validator
                                  if custom_validator is not None
                                  else
                                  lambda x: None)
        self._has_dir_dependencies = bool(self._value_computer.resolving_dependencies())

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        if not self._has_dir_dependencies:
            try:
                x = self._value_computer.value_when_no_dir_dependencies()
                return self._custom_validator(x)
            except NotAnIntegerException as ex:
                return text_docs.single_line(ex.value_string)

        return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        if self._has_dir_dependencies:
            try:
                x = self._value_computer.value_of_any_dependency(tcds)
                return self._custom_validator(x)
            except NotAnIntegerException as ex:
                return text_docs.single_line(ex.value_string)

        return None
