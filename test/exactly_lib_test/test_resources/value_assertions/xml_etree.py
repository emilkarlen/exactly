from typing import Mapping, Sequence, Optional
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def equals(expected: Element) -> Assertion[Element]:
    return asrt.and_([
        asrt.sub_component(
            'tag',
            _get_element_tag,
            asrt.equals(expected.tag),
        ),
        asrt.sub_component(
            'attributes',
            _get_element_attrib,
            asrt.equals(expected.attrib),
        ),
        asrt.sub_component(
            'text',
            _get_element_text,
            _text_assertion__none_eq_empty_str(expected.text),
        ),
        asrt.sub_component(
            'tail',
            _get_element_tail,
            _text_assertion__none_eq_empty_str(expected.tail),
        ),
        asrt.sub_component(
            'children',
            _get_element_children,
            asrt.matches_sequence__named([
                NameAndValue(repr(child.tag), equals(child))
                for child in list(expected)
            ]),
        ),
    ])


def str_as_xml_equals(expected: Element) -> Assertion[str]:
    return asrt.on_transformed2(
        ET.fromstring,
        equals(expected),
        'XML from string'
    )


def _text_assertion__none_eq_empty_str(expected: Optional[str]) -> Assertion[Optional[str]]:
    return (
        asrt.or_([
            asrt.is_none,
            asrt.equals('')
        ])
        if expected is None or expected == ''
        else
        asrt.equals(expected)
    )


def _get_element_tag(x: Element) -> str:
    return x.tag


def _get_element_text(x: Element) -> str:
    return x.text


def _get_element_tail(x: Element) -> str:
    return x.tail


def _get_element_attrib(x: Element) -> Mapping[str, str]:
    return x.attrib


def _get_element_children(x: Element) -> Sequence[Element]:
    return list(x)
