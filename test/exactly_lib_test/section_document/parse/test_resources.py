from typing import Dict, Sequence

from exactly_lib.section_document import model
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util import line_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def consume_current_line_and_return_it_as_line_sequence(source: ParseSource) -> line_source.LineSequence:
    ret_val = line_source.LineSequence(source.current_line_number,
                                       (source.current_line_text,))
    source.consume_current_line()
    return ret_val


def doc_to_dict(doc: model.Document) -> Dict[str, Sequence[model.SectionContentElement]]:
    return {section: doc.section_2_elements[section].elements
            for section in doc.section}


def matches_document(expected: Dict[str, Sequence[asrt.ValueAssertion[model.SectionContentElement]]]
                     ) -> asrt.ValueAssertion[model.Document]:
    expected_section_2_assertion = {section: asrt.matches_sequence(expected[section])
                                    for section in expected.keys()}

    assertion_on_dict = asrt.matches_dict(expected_section_2_assertion)
    return asrt.on_transformed(doc_to_dict, assertion_on_dict)
