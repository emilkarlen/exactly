from typing import Optional, Text, Sequence

from exactly_lib.util.textformat.structure import document as doc, core
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import Section, SectionContents, SectionItem
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def section_matches(header: Assertion[Text],
                    contents: Assertion[SectionContents],
                    target: Assertion[Optional[core.CrossReferenceTarget]] = asrt.anything_goes()
                    ) -> Assertion[Section]:
    return asrt.is_instance_with(
        Section,
        asrt.And([
            asrt.sub_component('target',
                               doc.Section.target.fget,
                               target),
            asrt.sub_component('header',
                               doc.Section.header.fget,
                               header),
            asrt.sub_component('contents',
                               doc.Section.contents.fget,
                               contents)
        ]))


def section_contents_matches(initial_paragraphs: Assertion[Sequence[ParagraphItem]] = asrt.anything_goes(),
                             sections: Assertion[Sequence[SectionItem]] = asrt.anything_goes()
                             ) -> Assertion[SectionContents]:
    return asrt.is_instance_with(
        SectionContents,
        asrt.And([
            asrt.sub_component('initial_paragraphs',
                               doc.SectionContents.initial_paragraphs.fget,
                               initial_paragraphs),
            asrt.sub_component('sections',
                               doc.SectionContents.sections.fget,
                               sections)
        ]))
