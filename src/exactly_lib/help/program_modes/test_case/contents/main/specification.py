from exactly_lib.help.program_modes.test_case.contents.main import ref_test_case_files as tc
from exactly_lib.help.program_modes.test_case.contents.main import ref_test_case_processing as processing
from exactly_lib.help.program_modes.test_case.contents.main import test_outcome
from exactly_lib.help.program_modes.test_case.contents.main.overview import renderer as overview
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils.rendering import section_hierarchy_rendering as hierarchy_rendering
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import \
    SectionContentsConstructorFromHierarchyGenerator
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def generator(header: str, test_case_help: TestCaseHelp) -> hierarchy_rendering.SectionHierarchyGenerator:
    setup = Setup(test_case_help)
    return hierarchy_rendering.parent(
        header,
        [],
        [
            ('overview', overview.generator('Overview', setup)),
            ('file-syntax', tc.generator('Test case file syntax', setup)),
            ('processing',
             hierarchy_rendering.leaf('Test case processing steps', processing.ContentsConstructor(setup))),
            ('outcome', test_outcome.hierarchy_generator('Test outcome', setup)),
        ])


def as_section_contents_renderer(test_case_help: TestCaseHelp) -> SectionContentsConstructor:
    return SectionContentsConstructorFromHierarchyGenerator(generator('unused header', test_case_help))
