from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.document import Section, SectionContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def section_matches(header: asrt.ValueAssertion,
                    contents: asrt.ValueAssertion,
                    target: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
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


def section_contents_matches(initial_paragraphs: asrt.ValueAssertion = asrt.anything_goes(),
                             sections: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
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
