from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_source(is_at_eof: asrt.ValueAssertion = asrt.anything_goes(),
                  is_at_eol: asrt.ValueAssertion = asrt.anything_goes(),
                  is_at_eol__except_for_space: asrt.ValueAssertion = asrt.anything_goes(),
                  has_current_line: asrt.ValueAssertion = asrt.anything_goes(),
                  current_line_number: asrt.ValueAssertion = asrt.anything_goes(),
                  current_line_text: asrt.ValueAssertion = asrt.anything_goes(),
                  remaining_part_of_current_line: asrt.ValueAssertion = asrt.anything_goes(),
                  remaining_source: asrt.ValueAssertion = asrt.anything_goes(),
                  ) -> asrt.ValueAssertion:
    return asrt.And([
        asrt.is_instance(ParseSource, 'Value to apply assertions on must be a {}'.format(ParseSource)),
        asrt.sub_component('is_at_eof', ParseSource.is_at_eof.fget, is_at_eof),
        asrt.sub_component('has_current_line', ParseSource.has_current_line.fget, has_current_line),
        asrt.Or([
            asrt.sub_component('has_current_line', ParseSource.has_current_line.fget, asrt.equals(False)),
            # The following must only be checked if has_current_line (because of precondition of ParseSource):
            asrt.And([
                asrt.sub_component('is_at_eol', ParseSource.is_at_eol.fget, is_at_eol),
                asrt.sub_component('is_at_eol__except_for_space', ParseSource.is_at_eol__except_for_space.fget,
                                   is_at_eol__except_for_space),
                asrt.sub_component('current_line_number', ParseSource.current_line_number.fget, current_line_number),
                asrt.sub_component('current_line_text', ParseSource.current_line_text.fget, current_line_text),
                asrt.sub_component('remaining_part_of_current_line', ParseSource.remaining_part_of_current_line.fget,
                                   remaining_part_of_current_line),
            ])
        ]),
        asrt.sub_component('remaining_source', ParseSource.remaining_source.fget, remaining_source),
    ])


source_is_at_end = assert_source(is_at_eof=asrt.Boolean(True),
                                 has_current_line=asrt.Boolean(False),
                                 remaining_source=asrt.equals('')
                                 )


def source_is_not_at_end(is_at_eol: asrt.ValueAssertion = asrt.anything_goes(),
                         current_line_number: asrt.ValueAssertion = asrt.anything_goes(),
                         current_line_text: asrt.ValueAssertion = asrt.anything_goes(),
                         remaining_part_of_current_line: asrt.ValueAssertion = asrt.anything_goes(),
                         remaining_source: asrt.ValueAssertion = asrt.anything_goes(),
                         ) -> asrt.ValueAssertion:
    return assert_source(
        is_at_eof=asrt.is_false,
        has_current_line=asrt.is_true,
        is_at_eol=is_at_eol,
        current_line_number=current_line_number,
        current_line_text=current_line_text,
        remaining_part_of_current_line=remaining_part_of_current_line,
        remaining_source=remaining_source,
    )
