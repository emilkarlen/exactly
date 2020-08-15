import unittest
from copy import copy
from typing import Dict, Optional, List, Sequence, Callable
from xml.etree import ElementTree as ET

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import xml_etree as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsElementWithoutChildren),
        unittest.makeSuite(TestEqualsElementWithChildren),
        unittest.makeSuite(TestStrAsXmlEquals),
    ])


class TestEqualsElementWithoutChildren(unittest.TestCase):
    EQUIVALENT_STR_CASES = [
        NEA(
            'expected=None, actual=empty string',
            expected=None,
            actual='',
        ),
        NEA(
            'expected=empty string , actual=None',
            expected='',
            actual=None,
        ),
    ]

    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_equals(self):
        for case in equal_element_cases():
            with self.subTest(case.name):
                actual = copy(case.value)
                sut.equals(case.value).apply_without_message(self.put, actual)

    def test_not_equals(self):
        for case in unequal_element_cases():
            with self.subTest(case.name):
                with self.assertRaises(TestException):
                    sut.equals(case.expected).apply_without_message(self.put, case.actual)

    def test_text__none_and_empty_str_are_equivalent(self):
        for case in self.EQUIVALENT_STR_CASES:
            with self.subTest(case.name):
                expected = _elem('tag', text=case.expected)
                actual = _elem(expected.tag, text=case.actual)
                sut.equals(expected).apply_without_message(self, actual)

    def test_tail__none_and_empty_str_are_equivalent(self):
        for case in self.EQUIVALENT_STR_CASES:
            with self.subTest(case.name):
                expected = _elem('tag', tail=case.expected)
                actual = _elem(expected.tag, tail=case.actual)
                sut.equals(expected).apply_without_message(self, actual)


class TestEqualsElementWithChildren(unittest.TestCase):

    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_equals(self):
        for children_level_case in CHILDREN_LEVEL_CASES:
            for expected_child in equal_element_cases():
                actual_child = copy(expected_child.value)
                for child_seq_case in _equivalent_child_sequence_variants():
                    with self.subTest(children_level_case=children_level_case.name,
                                      expected_child=expected_child.name,
                                      child_seq=child_seq_case.name):
                        expected = children_level_case.value(child_seq_case.value(expected_child.value))
                        actual = children_level_case.value(child_seq_case.value(actual_child))
                        sut.equals(expected).apply_without_message(self.put, actual)

    def test_not_equals__single_child(self):
        for children_level_case in CHILDREN_LEVEL_CASES:
            for case in unequal_element_cases():
                with self.subTest(children_level_case=children_level_case.name,
                                  unequal_child=case.name):
                    expected = children_level_case.value([case.expected])
                    actual = children_level_case.value([case.actual])
                    with self.assertRaises(TestException):
                        sut.equals(expected).apply_without_message(self.put, actual)

    def test_not_equals__num_children(self):
        child_name = 'child-name'
        cases__pos_dir = [
            NEA('expected: 0',
                [],
                [_elem(child_name)],
                ),
            NEA('expected: 1',
                [_elem(child_name)],
                [_elem(child_name), _elem(child_name)],
                ),
            NEA('expected: 2',
                [_elem(child_name), _elem(child_name)],
                [_elem(child_name), _elem(child_name), _elem(child_name), _elem(child_name)],
                ),
        ]

        for children_level_case in CHILDREN_LEVEL_CASES:
            cases = _with_positive_and_negative_direction([
                NEA(c.name,
                    children_level_case.value(c.expected),
                    children_level_case.value(c.actual),
                    )
                for c in cases__pos_dir
            ])
            for case in cases:
                with self.subTest(children_level_case=children_level_case.name,
                                  children_sequence=case.name):
                    with self.assertRaises(TestException):
                        sut.equals(case.expected).apply_without_message(self.put, case.actual)


class TestStrAsXmlEquals(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_equals(self):
        for case in equal_element_cases__wo_tail():
            with self.subTest(case.name):
                actual = ET.tostring(case.value, encoding="unicode")
                sut.str_as_xml_equals(case.value).apply_without_message(self.put, actual)

    def test_not_equals(self):
        for case in unequal_element_cases(include_syntactically_incorrect_tail_cases=False):
            with self.subTest(case.name):
                actual__as_str = ET.tostring(case.actual, encoding="unicode")
                with self.assertRaises(TestException):
                    sut.str_as_xml_equals(case.expected).apply_without_message(self.put, actual__as_str)


def equal_element_cases() -> List[NameAndValue[ET.Element]]:
    tag = 'the-tag'
    return [
        NameAndValue(
            'text={text}, tail={tail}, attrs={attrs}'.format(
                text=repr(text),
                tail=repr('tail'),
                attrs=attributes,
            ),
            _elem(tag, text=text, tail=tail, attributes=attributes)
        )
        for text in [None, 'some text']
        for tail in [None, 'some tail']
        for attributes in [{}, {'key': 'value'}]
    ]


def equal_element_cases__wo_tail() -> List[NameAndValue[ET.Element]]:
    tag = 'the-tag'
    return [
        NameAndValue(
            'text={text}, attrs={attrs}'.format(
                text=repr(text),
                attrs=attributes,
            ),
            _elem(tag, text=text, attributes=attributes)
        )
        for text in [None, 'some text']
        for attributes in [{}, {'key': 'value'}]
    ]


def unequal_element_cases(include_syntactically_incorrect_tail_cases: bool = True) -> List[NEA[ET.Element, ET.Element]]:
    ret_val = (
            unequal_tag_cases() +
            unequal_text_cases() +
            unequal_attributes_cases()
    )
    if include_syntactically_incorrect_tail_cases:
        ret_val += unequal_tail_cases()

    return ret_val


def unequal_tag_cases() -> List[NEA[ET.Element, ET.Element]]:
    tag = 'the-tag'
    return [
        NEA('unequal-tag',
            _elem(tag, text='a'),
            _elem(tag, text='ab'),
            )
    ]


def unequal_text_cases() -> List[NEA[ET.Element, ET.Element]]:
    return [
        NEA('unequal-text',
            _elem('expected'),
            _elem('actual'),
            )
    ]


def unequal_tail_cases() -> List[NEA[ET.Element, ET.Element]]:
    tag = 'the-tag'
    return [
        NEA('unequal-tail',
            _elem(tag, tail='a'),
            _elem(tag, tail='ab'),
            )
    ]


def unequal_attributes_cases() -> List[NEA[ET.Element, ET.Element]]:
    cases_positive_direction = [
        NEA(
            'number of attributes / one empty',
            {},
            {'a': 'A'}
        ),
        NEA(
            'number of attributes / no one empty',
            {'a': 'A'},
            {'a': 'A', 'b': 'A'},
        ),
        NEA(
            'non-empty set of attributes / diff key',
            {'a': 'value'},
            {'b': 'value'},
        ),
        NEA(
            'non-empty set of attributes / diff value',
            {'a': 'value 1'},
            {'a': 'value 2'},
        ),
    ]
    tag = 'attr-test'
    return _with_positive_and_negative_direction([
        NEA(c.name,
            _elem(tag, c.expected),
            _elem(tag, c.actual),
            )
        for c in cases_positive_direction
    ])


def _with_positive_and_negative_direction(positive_dir: List[NEA[ET.Element, ET.Element]],
                                          ) -> List[NEA[ET.Element, ET.Element]]:
    return (
            positive_dir
            +
            [
                NEA(c.name + ' - negative direction', c.actual, c.expected)
                for c in positive_dir
            ]
    )


def _equivalent_child_sequence_variants() -> List[NameAndValue[Callable[[ET.Element], Sequence[ET.Element]]]]:
    return [
        NameAndValue(
            'single child',
            lambda child: [child],
        ),
        NameAndValue(
            'preceded by single element',
            lambda child: [_elem('preceding'), child],
        ),
        NameAndValue(
            'followed by single element',
            lambda child: [child, _elem('following')],
        ),
    ]


def _mk_children_at_lvl_1(children: Sequence[ET.Element]) -> ET.Element:
    return _elem('root', children=children)


def _mk_children_at_lvl_2(children: Sequence[ET.Element]) -> ET.Element:
    return _elem('root', children=[_elem('level-1', children=children)])


CHILDREN_LEVEL_CASES = [
    NameAndValue(
        'children at level 1',
        _mk_children_at_lvl_1,
    ),
    NameAndValue(
        'children at level 2',
        _mk_children_at_lvl_2,
    ),
]


def _elem(tag: str,
          attributes: Optional[Dict[str, str]] = None,
          text: Optional[str] = None,
          tail: Optional[str] = None,
          children: Sequence[ET.Element] = (),
          ) -> ET.Element:
    ret_val = ET.Element(tag)

    if attributes is not None:
        ret_val.attrib.update(attributes)

    ret_val.text = text
    ret_val.tail = tail

    ret_val.extend(children)

    return ret_val
