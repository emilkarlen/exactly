import unittest

from exactly_lib.help.cross_reference_id import TargetInfo, TargetInfoNode, target_info_leaf
from exactly_lib.help.utils import table_of_contents as sut
from exactly_lib.util.textformat.structure import lists
from exactly_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import CrossReferenceTarget
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestTocList)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestTocList(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        hierarchy = []
        # ACT #
        actual = sut.toc_list(hierarchy, LIST_TYPE)
        # ASSERT #
        struct_check.is_header_value_list.apply(self, actual)

    def test_singleton(self):
        # ARRANGE #
        hierarchy = [target_info_leaf(TI)]
        # ACT #
        actual = sut.toc_list(hierarchy, LIST_TYPE)
        # ASSERT #
        struct_check.is_header_value_list.apply(self, actual)

    def test_multiple(self):
        # ARRANGE #
        hierarchy = [
            target_info_leaf(TI),
            target_info_leaf(TI),
        ]
        # ACT #
        actual = sut.toc_list(hierarchy, LIST_TYPE)
        # ASSERT #
        struct_check.is_header_value_list.apply(self, actual)

    def test_nested(self):
        # ARRANGE #
        hierarchy = [
            TargetInfoNode(TI, [
                target_info_leaf(TI),
            ])
        ]
        # ACT #
        actual = sut.toc_list(hierarchy, LIST_TYPE)
        # ASSERT #
        struct_check.is_header_value_list.apply(self, actual)


LIST_TYPE = lists.ListType.ITEMIZED_LIST

TI = TargetInfo('presentation',
                CrossReferenceTarget('target'))
