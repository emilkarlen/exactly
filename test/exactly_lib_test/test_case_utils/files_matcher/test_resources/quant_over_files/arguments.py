from typing import Optional

from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building2 as sm_arg


def file_contents_arg2(
        contents_variant: sm_arg.StringMatcherArg,
        transformer: Optional[str] = None
) -> fm_args.WithOptionalNegation:
    if transformer is not None:
        contents_variant = sm_arg.Transformed(transformer, contents_variant)
    return fm_args.WithOptionalNegation(fm_args.Contents(contents_variant))
