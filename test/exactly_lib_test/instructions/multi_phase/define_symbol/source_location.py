import pathlib
import unittest

from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.section_document.source_location import FileSystemLocationInfo, FileLocationInfo, SourceLocation, \
    SourceLocationPath
from exactly_lib.symbol.sdv_structure import SymbolDefinition
from exactly_lib.util.line_source import LineSequence, single_line_sequence
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.source_formatting import single_line_source
from exactly_lib_test.section_document.test_resources.source_location_assertions import matches_source_location_info, \
    equals_source_location_path
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulDefinition),
    ])


class TestSuccessfulDefinition(unittest.TestCase):
    def test_assignment_of_single_constant_word(self):
        # ARRANGE #

        source = single_line_source('{string_type} name1 = v1')
        source_string = source.source_string

        parser = sut.EmbryoParser()

        the_file_path_rel_referrer = pathlib.Path('the-path-rel-referrer')
        the_file_location_info = FileLocationInfo(
            pathlib.Path.cwd(),
            the_file_path_rel_referrer,
            [
                SourceLocation(LineSequence(10, ('line-in-inclusion-chain',)),
                               pathlib.Path('the-path-rel-referrer-of-first-file'))
            ])
        fs_location_info = FileSystemLocationInfo(the_file_location_info)

        # ACT #

        instruction = parser.parse(fs_location_info, source)

        # ASSERT #

        expected_source_location_path = SourceLocationPath(
            SourceLocation(single_line_sequence(1, source_string),
                           the_file_path_rel_referrer),
            the_file_location_info.file_inclusion_chain,
        )

        assertion = matches_source_location_info(
            abs_path_of_dir_containing_first_file_path=asrt.equals(
                the_file_location_info.abs_path_of_dir_containing_first_file_path),
            source_location_path=equals_source_location_path(expected_source_location_path)
        )

        # ASSERT SANITY #

        assert 1 == len(instruction.symbol_usages), 'A single symbol should have been defined'

        symbol_definition = instruction.symbol_usages[0]

        assert isinstance(symbol_definition, SymbolDefinition)

        assertion.apply_without_message(self, symbol_definition.symbol_container.source_location)
