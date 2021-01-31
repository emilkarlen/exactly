from exactly_lib.symbol import value_type
from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib.symbol.value_type import TypeCategory, ValueType
from exactly_lib.type_val_deps.sym_ref.restrictions import TypeCategoryRestriction, ValueTypeRestriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def is_type_category_restriction(expected: TypeCategory) -> Assertion[ReferenceRestrictions]:
    """
    Assertion on a :class:`ReferenceRestrictions`,
    that it is a :class:`TypeCategoryRestriction`,
    with a given :class:`TypeCategory`.
    """
    return asrt.is_instance_with(TypeCategoryRestriction,
                                 asrt.sub_component('type_category',
                                                    TypeCategoryRestriction.type_category.fget,
                                                    asrt.is_(expected)))


def is_value_type_restriction(expected: ValueType) -> Assertion[ReferenceRestrictions]:
    """
    Assertion on a :class:`ReferenceRestrictions`,
    that it is a :class:`TypeCategoryRestriction`,
    with a given :class:`TypeCategory`.
    """
    expected_type_category = value_type.VALUE_TYPE_2_TYPE_CATEGORY[expected]
    return asrt.is_instance_with(ValueTypeRestriction,
                                 asrt.and_([
                                     asrt.sub_component('value_type',
                                                        ValueTypeRestriction.value_type.fget,
                                                        asrt.is_(expected)),
                                     asrt.sub_component('type_category',
                                                        ValueTypeRestriction.type_category.fget,
                                                        asrt.is_(expected_type_category)),
                                 ]),
                                 )
