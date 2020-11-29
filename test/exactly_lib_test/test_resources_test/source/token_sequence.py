import unittest
from typing import Sequence, AbstractSet

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.source.layout import LayoutSpec, LayoutAble, TokenPosition
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence, Token
from exactly_lib_test.test_resources.string_formatting import StringFormatter
from exactly_lib_test.test_resources.test_utils import NArrEx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestLayout(),
        TestNewLine(),
        TestEmpty(),
        TestSingleton(),
        TestSequence(),
        TestConcat(),
    ])


class Case:
    def __init__(self,
                 name: str,
                 tokens: Sequence[Token],
                 layout: LayoutSpec,
                 expected: str,
                 ):
        self.name = name
        self.tokens = tokens
        self.layout = layout
        self.expected = expected


class TestLayout(unittest.TestCase):
    def runTest(self):
        opt_new_line = '<OPT-NEW-LINE>'
        token_sep = '<TOKEN-SEPARATOR>'
        layout = LayoutSpec(
            optional_new_line=(opt_new_line,),
            symbol_reference_as_plain_symbol_name=False,
            token_separator=token_sep,
        )
        layout_formatter = StringFormatter({
            'opt_nl': opt_new_line,
            'token_sep': token_sep
        })
        cases = [
            Case('empty',
                 [],
                 layout,
                 '',
                 ),
            Case('single empty token',
                 [''],
                 layout,
                 '',
                 ),
            Case('single white space token',
                 ['  '],
                 layout,
                 '  ',
                 ),
            Case('single new-line token',
                 ['\n'],
                 layout,
                 '\n',
                 ),
            Case('single token with embedded new-line',
                 ['before\nafter'],
                 layout,
                 'before\nafter',
                 ),
            Case('single non-empty/white space token',
                 ['the-token'],
                 layout,
                 'the-token',
                 ),
            Case('{LayoutAble} objects should be rendered using their rendering method'.format(LayoutAble=LayoutAble),
                 [_LayoutAbleThatGivesOptionalNewLineStrings()],
                 layout,
                 layout_formatter.format('{opt_nl}'),
                 ),
            Case('single empty layout-able',
                 [_ConstLayoutAble([])],
                 layout,
                 '',
                 ),
            Case('single layout-able w single empty element',
                 [_ConstLayoutAble([''])],
                 layout,
                 '',
                 ),
            Case('two tokens, should be separated by the token separator',
                 ['t1', 't2'],
                 layout,
                 layout_formatter.format('t1{token_sep}t2'),
                 ),
            Case('empty tokens should be ignored',
                 ['', 'T1', '', '', 'T2', '', 'T3', '', _ConstLayoutAble(['', 'T4', ''])],
                 layout,
                 layout_formatter.format('T1{token_sep}T2{token_sep}T3{token_sep}T4'),
                 ),
            Case('the token separator should not be be added beside new-line tokens',
                 ['\n', 'T'],
                 layout,
                 '\nT',
                 ),
            Case('the token separator should not be be added beside new-lines',
                 ['S\n', 'T'],
                 layout,
                 'S\nT',
                 ),
            Case('the token separator should not be be added beside new-lines',
                 ['S', 'T\n', 'U'],
                 layout,
                 layout_formatter.format('S{token_sep}T\nU'),
                 ),
            Case('the token separator should not be be added beside new-lines',
                 ['T', '\n'],
                 layout,
                 'T\n',
                 ),
            Case('the token separator should not be be added beside new-lines',
                 ['T', '\nU'],
                 layout,
                 'T\nU',
                 ),
            Case('the token separator should not be be added beside new-lines',
                 ['\n', '\n'],
                 layout,
                 '\n\n',
                 ),
            Case('token position / single token',
                 [_LayoutAbleThatChecksTokenPositionArgument(
                     self,
                     {TokenPosition.FIRST, TokenPosition.LAST},
                     ''),
                 ],
                 layout,
                 '',
                 ),
            Case('token position / multiple tokens',
                 [
                     _LayoutAbleThatChecksTokenPositionArgument(
                         self,
                         {TokenPosition.FIRST},
                         '',
                     ),
                     _LayoutAbleThatChecksTokenPositionArgument(
                         self,
                         set(),
                         '',
                     ),
                     'string-token',
                     _LayoutAbleThatChecksTokenPositionArgument(
                         self,
                         set(),
                         '',
                     ),
                     _LayoutAbleThatChecksTokenPositionArgument(
                         self,
                         {TokenPosition.LAST},
                         '',
                     ),
                 ],
                 layout,
                 'string-token',
                 ),
        ]
        for case in cases:
            with self.subTest(case=case.name,
                              tokens=repr(case.tokens)):
                tok_seq = _ConstTokSeqTestImpl(case.tokens)
                # ACT #
                actual = tok_seq.layout(case.layout)
                # ASSERT #
                self.assertEqual(case.expected, actual)


class TestNewLine(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'layout spec w optional-new line as empty',
                LAYOUT_SPEC__OPTIONAL_NEW_LINE_AS_EMPTY,
            ),
            NameAndValue(
                'layout spec w optional new-line as new-line',
                LAYOUT_SPEC__OPTIONAL_NEW_LINE_AS_NEW_LINE,
            ),
        ]

        tok_seq = TokenSequence.new_line()
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = tok_seq.layout(case.value)
                # ASSERT #
                self.assertEqual('\n', actual)


class TestOptionalNewLine(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NArrEx(
                'layout spec w optional-new line as empty',
                LAYOUT_SPEC__OPTIONAL_NEW_LINE_AS_EMPTY,
                '',
            ),
            NArrEx(
                'layout spec w optional new-line as new-line',
                LAYOUT_SPEC__OPTIONAL_NEW_LINE_AS_NEW_LINE,
                '\n',
            ),
        ]

        tok_seq = TokenSequence.optional_new_line()
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = tok_seq.layout(case.arrangement)
                # ASSERT #
                self.assertEqual(case.expectation, actual)


class TestEmpty(unittest.TestCase):
    def runTest(self):
        actual = TokenSequence.empty().tokens
        self.assertEqual((), actual)


class TestSingleton(unittest.TestCase):
    def runTest(self):
        actual = TokenSequence.singleton('T').tokens
        self.assertEqual(('T',), actual)


class TestSequence(unittest.TestCase):
    def runTest(self):
        tokens = ['T1', 'T2']
        actual = TokenSequence.sequence(tokens).tokens
        self.assertEqual(tokens, actual)


class TestConcat(unittest.TestCase):
    def runTest(self):
        tokens_s = ['S1', 'S2']
        tokens_t = ['T1', 'T2']
        concat = TokenSequence.concat([
            _ConstTokSeqTestImpl(tokens_s),
            _ConstTokSeqTestImpl(tokens_t),
        ])
        actual = concat.tokens
        self.assertEqual(tokens_s + tokens_t, actual)


class _ConstTokSeqTestImpl(TokenSequence):
    def __init__(self, tokens: Sequence[Token]):
        self._tokens = tokens

    @property
    def tokens(self) -> Sequence[Token]:
        return self._tokens


class _LayoutAbleThatGivesOptionalNewLineStrings(LayoutAble):
    def layout(self,
               spec: LayoutSpec,
               position: AbstractSet[TokenPosition],
               ) -> Sequence[str]:
        return spec.optional_new_line


class _ConstLayoutAble(LayoutAble):
    def __init__(self, values: Sequence[str]):
        self.values = values

    def layout(self,
               spec: LayoutSpec,
               position: AbstractSet[TokenPosition],
               ) -> Sequence[str]:
        return self.values


class _LayoutAbleThatChecksTokenPositionArgument(LayoutAble):
    def __init__(self,
                 put: unittest.TestCase,
                 expected: AbstractSet[TokenPosition],
                 values: Sequence[str]):
        self.put = put
        self.expected = expected
        self.values = values

    def layout(self,
               spec: LayoutSpec,
               position: AbstractSet[TokenPosition],
               ) -> Sequence[str]:
        self.put.assertEqual(self.expected, position, 'token position')
        return self.values


LAYOUT_SPEC__OPTIONAL_NEW_LINE_AS_EMPTY = LayoutSpec((), False, ' ')
LAYOUT_SPEC__OPTIONAL_NEW_LINE_AS_NEW_LINE = LayoutSpec(('\n',), False, ' ')

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
