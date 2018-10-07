from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcher
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherConstantResolver
from exactly_lib.util.logic_types import ExpectationType


def emptiness_via_string_matcher(expectation_type: ExpectationType) -> FileContentsAssertionPart:
    matcher_resolver = StringMatcherConstantResolver(
        EmptinessStringMatcher(expectation_type)
    )
    return StringMatcherAssertionPart(matcher_resolver)
