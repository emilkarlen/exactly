from typing import Sequence

from exactly_lib.tcfs.path_relativity import DEPENDENCY_DICT, DirectoryStructurePartition, \
    RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.copy_.test_resources import argument_syntax as args
from exactly_lib_test.impls.instructions.multi_phase.copy_.test_resources import defs
from exactly_lib_test.tcfs.test_resources.path_arguments import RelOptPathArgument
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer

INVALI_SYNTAX_CASES = [
    NameAndValue('no arguments', ''),
    NameAndValue('superfluous arguments', 'src dst superfluous'),
]


def illegal_relativities_independent_of_phase() -> Sequence[NameAndValue[ArgumentElementsRenderer]]:
    dst_illegal_relativities = DEPENDENCY_DICT[DirectoryStructurePartition.HDS]
    return [
        NameAndValue(
            'illegal dst relativity: {}'.format(dst_illegal),
            args.copy(RelOptPathArgument('src-file-name', defs.ARBITRARY_LEGAL_RELATIVITY__SRC),
                      RelOptPathArgument('dst-file-name', dst_illegal))
        )
        for dst_illegal in dst_illegal_relativities
    ]


def illegal_relativities_specific_for_phase_before_act() -> Sequence[NameAndValue[ArgumentElementsRenderer]]:
    dst_illegal_relativities = {RelOptionType.REL_RESULT}
    return [
        NameAndValue(
            'illegal dst relativity: {}'.format(dst_illegal),
            args.copy(RelOptPathArgument('src-file-name', defs.ARBITRARY_LEGAL_RELATIVITY__SRC),
                      RelOptPathArgument('dst-file-name', dst_illegal))
        )
        for dst_illegal in dst_illegal_relativities
    ]


def legal_relativities_independent_of_phase() -> Sequence[NameAndValue[ArgumentElementsRenderer]]:
    src_legal_relativities = (
            set(RelOptionType) - {RelOptionType.REL_RESULT}
    )
    dst_legal_relativities = (
            DEPENDENCY_DICT[DirectoryStructurePartition.NON_HDS] - {RelOptionType.REL_RESULT}
    )

    ret_val = []
    ret_val += [
        NameAndValue('only src:{}'.format(relativity),
                     args.copy(RelOptPathArgument('src-file-name', relativity)))
        for relativity in src_legal_relativities
    ]
    ret_val += [
        NameAndValue('src:{}, dst:{}'.format(src_relativity, dst_relativity),
                     args.copy(RelOptPathArgument('src-file-name', src_relativity),
                               RelOptPathArgument('dst-file-name', dst_relativity)))
        for src_relativity in src_legal_relativities
        for dst_relativity in dst_legal_relativities
    ]
    return ret_val


def legal_relativities_specific_for_phases_after_act() -> Sequence[NameAndValue[ArgumentElementsRenderer]]:
    src_legal = RelOptionType.REL_RESULT
    return [
        NameAndValue('legal src:{}'.format(src_legal),
                     args.copy(RelOptPathArgument('src-file-name', src_legal),
                               RelOptPathArgument('dst-file-name', defs.ARBITRARY_LEGAL_RELATIVITY__DST)
                               ),
                     )
    ]
