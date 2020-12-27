from typing import Sequence

from exactly_lib.impls.types.string_source.source_from_contents import StringSourceWConstantContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.type_val_prims.string_source.test_resources import string_source_base
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_contents import \
    StringSourceContentsFromLines


def source_from_lines_test_impl(raw_lines: Sequence[str],
                                tmp_file_space: DirFileSpace,
                                may_depend_on_external_resources: bool = False,
                                ) -> StringSource:
    return StringSourceWConstantContents(
        string_source_base.new_structure_builder,
        StringSourceContentsFromLines(raw_lines,
                                      tmp_file_space,
                                      may_depend_on_external_resources),
    )
