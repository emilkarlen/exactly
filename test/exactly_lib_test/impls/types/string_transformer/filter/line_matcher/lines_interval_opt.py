import unittest
from typing import Sequence

from exactly_lib.impls.types.condition import comparators
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.integer_matcher.test_resources import argument_building as im_args
from exactly_lib_test.impls.types.line_matcher.test_resources import arguments_building as lm_arg
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as sm_args
from exactly_lib_test.impls.types.string_source.test_resources.argument_renderers import FileOrString
from exactly_lib_test.impls.types.string_transformer.filter.line_matcher import test_resources as tr
from exactly_lib_test.impls.types.string_transformer.filter.line_matcher.test_resources import IntSymbol, \
    ModelAndArguments, _from_to, Case
from exactly_lib_test.impls.types.test_resources import arguments_building as arg_rend
from exactly_lib_test.test_resources.argument_renderer import SymbolReferenceWReferenceSyntax


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestJustLineNumWNonComplexExpression),
        unittest.makeSuite(TestJustLineNumWComplexExpression),
        unittest.makeSuite(TestLineNumAndContents),
        unittest.makeSuite(TestContents),
    ])


class TestJustLineNumWNonComplexExpression(unittest.TestCase):
    def test_point(self):
        int_sym = IntSymbol('eq_value')
        arguments = tr.filter_line_num(
            im_args.comparison(comparators.EQ, SymbolReferenceWReferenceSyntax(int_sym.name))
        )
        m10 = ModelAndArguments(tr.model_lines(10), arguments)
        tr.check_cases__named(
            self,
            [
                m10.case__n(
                    [int_sym.value(1)],
                    max_num_lines_from_iter=1,
                    expected_output_lines=[1],
                ),
                m10.case__n(
                    [int_sym.value(5)],
                    max_num_lines_from_iter=5,
                    expected_output_lines=[5],
                ),
                m10.case__n(
                    [int_sym.value(10)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=[10],
                ),
                m10.case__n(
                    [int_sym.value(11)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=[],
                ),
            ] +
            m10.equivalent_cases__n([
                [int_sym.value(0)],
                [int_sym.value(-1)],
            ],
                max_num_lines_from_iter=0,
                expected_output_lines=[],
            )
        )

    def test_upper_limit(self):
        upper_limit = IntSymbol('UPPER_LIMIT')
        arguments = tr.filter_line_num(
            im_args.comparison(comparators.LTE, SymbolReferenceWReferenceSyntax(upper_limit.name))
        )
        m10 = ModelAndArguments(tr.model_lines(10), arguments)
        tr.check_cases__named(
            self,
            [
                m10.case__n(
                    [upper_limit.value(-3)],
                    max_num_lines_from_iter=0,
                    expected_output_lines=[],
                ),
                m10.case__n(
                    [upper_limit.value(1)],
                    max_num_lines_from_iter=1,
                    expected_output_lines=[1],
                ),
                m10.case__n(
                    [upper_limit.value(5)],
                    max_num_lines_from_iter=5,
                    expected_output_lines=_from_to(1, 5),
                ),
            ] +
            m10.equivalent_cases__n([
                [upper_limit.value(10)],
                [upper_limit.value(10 + 1)],
            ],
                max_num_lines_from_iter=10,
                expected_output_lines=_from_to(1, 10),
            )
        )

    def test_lower_limit(self):
        lower_limit = IntSymbol('LOWER_LIMIT')
        arguments = tr.filter_line_num(
            im_args.comparison(comparators.GTE, SymbolReferenceWReferenceSyntax(lower_limit.name))
        )
        m10 = ModelAndArguments(tr.model_lines(10), arguments)
        cases = _cases_for_lower_limit(m10, lower_limit)
        tr.check_cases__named(
            self,
            cases,
        )


class TestJustLineNumWComplexExpression(unittest.TestCase):
    def test_finite_w_conjunction_of_line_matchers(self):
        # ARRANGE #
        lower_limit = IntSymbol('lower_limit')
        upper_limit = IntSymbol('upper_limit')
        arguments = tr.filter_lm__within_parens(
            arg_rend.conjunction([
                lm_arg.LineNum2(
                    im_args.comparison(
                        comparators.GTE,
                        SymbolReferenceWReferenceSyntax(lower_limit.name)
                    )),
                lm_arg.LineNum2(
                    im_args.comparison(
                        comparators.LTE,
                        SymbolReferenceWReferenceSyntax(upper_limit.name)
                    )),
            ])
        )
        m10 = ModelAndArguments(tr.model_lines(10), arguments)
        cases = self._finite_w_conjunction__cases(m10, lower_limit, upper_limit)
        # ACT & ASSET #
        tr.check_cases__named(
            self,
            cases,
        )

    def test_finite_w_conjunction_of_integer_matchers(self):
        # ARRANGE #
        lower_limit = IntSymbol('lower_limit')
        upper_limit = IntSymbol('upper_limit')
        arguments = tr.filter_lm(lm_arg.LineNum2(
            arg_rend.within_paren(
                arg_rend.conjunction([
                    im_args.comparison(
                        comparators.GTE,
                        SymbolReferenceWReferenceSyntax(lower_limit.name)
                    ),
                    im_args.comparison(
                        comparators.LTE,
                        SymbolReferenceWReferenceSyntax(upper_limit.name)
                    ),
                ]))
        ))
        m10 = ModelAndArguments(tr.model_lines(10), arguments)
        cases = self._finite_w_conjunction__cases(m10, lower_limit, upper_limit)
        # ACT & ASSET #
        tr.check_cases__named(
            self,
            cases,
        )

    def test_disjunction_of_line_matchers(self):
        eq_1 = IntSymbol('EQ_1')
        eq_2 = IntSymbol('EQ_2')
        arguments = tr.filter_lm__within_parens(
            arg_rend.disjunction([
                lm_arg.LineNum2(
                    im_args.comparison(
                        comparators.EQ,
                        SymbolReferenceWReferenceSyntax(eq_1.name)
                    )),
                lm_arg.LineNum2(
                    im_args.comparison(
                        comparators.EQ,
                        SymbolReferenceWReferenceSyntax(eq_2.name)
                    )),
            ])
        )
        m10 = ModelAndArguments(tr.model_lines(10), arguments)
        tr.check_cases__named(
            self,
            [
                m10.case__n(
                    [eq_1.value(-10), eq_2.value(-5)],
                    max_num_lines_from_iter=0,
                    expected_output_lines=[],
                ),
                m10.case__n(
                    [eq_1.value(-10), eq_2.value(5)],
                    max_num_lines_from_iter=5,
                    expected_output_lines=[5],
                ),
                m10.case__n(
                    [eq_1.value(-10), eq_2.value(10 + 1)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=[],
                ),
                m10.case__n(
                    [eq_1.value(2), eq_2.value(5)],
                    max_num_lines_from_iter=5,
                    expected_output_lines=[2, 5],
                ),
                m10.case__n(
                    [eq_1.value(2), eq_2.value(10 + 1)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=[2],
                ),
                m10.case__n(
                    [eq_1.value(10 + 1), eq_2.value(10 + 2)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=[],
                ),
            ]
        )

    def test_negation_of_line_matcher(self):
        lower_limit = IntSymbol('NEGATED_UPPER_LIMIT__OPEN')
        arguments = tr.filter_line_num(
            arg_rend.negation(
                im_args.comparison(comparators.LT, SymbolReferenceWReferenceSyntax(lower_limit.name))
            )
        )
        m10 = ModelAndArguments(tr.model_lines(10), arguments)
        cases = _cases_for_lower_limit(m10, lower_limit)
        tr.check_cases__named(
            self,
            cases,
        )

    @staticmethod
    def _finite_w_conjunction__cases(model_w_10_elems: ModelAndArguments,
                                     lower_limit: IntSymbol,
                                     upper_limit: IntSymbol,
                                     ) -> Sequence[NameAndValue[Case]]:
        return (
                [
                    model_w_10_elems.case__n(
                        [lower_limit.value(-2), upper_limit.value(1)],
                        max_num_lines_from_iter=1,
                        expected_output_lines=[1],
                    ),
                    model_w_10_elems.case__n(
                        [lower_limit.value(-2), upper_limit.value(5)],
                        max_num_lines_from_iter=5,
                        expected_output_lines=_from_to(1, 5),
                    ),
                    model_w_10_elems.case__n(
                        [lower_limit.value(-2), upper_limit.value(10)],
                        max_num_lines_from_iter=10,
                        expected_output_lines=_from_to(1, 10),
                    ),
                    model_w_10_elems.case__n(
                        [lower_limit.value(-2), upper_limit.value(10 + 1)],
                        max_num_lines_from_iter=10,
                        expected_output_lines=_from_to(1, 10),
                    ),
                    model_w_10_elems.case__n(
                        [lower_limit.value(1), upper_limit.value(3)],
                        max_num_lines_from_iter=3,
                        expected_output_lines=_from_to(1, 3),
                    ),
                    model_w_10_elems.case__n(
                        [lower_limit.value(2), upper_limit.value(3)],
                        max_num_lines_from_iter=3,
                        expected_output_lines=_from_to(2, 3),
                    ),
                    model_w_10_elems.case__n(
                        [lower_limit.value(10), upper_limit.value(10 + 1)],
                        max_num_lines_from_iter=10,
                        expected_output_lines=[10],
                    ),
                    model_w_10_elems.case__n(
                        [lower_limit.value(10 + 1), upper_limit.value(10 + 2)],
                        max_num_lines_from_iter=10,
                        expected_output_lines=[],
                    ),
                ] +
                model_w_10_elems.equivalent_cases__n([
                    [lower_limit.value(1 - 2), upper_limit.value(10)],
                    [lower_limit.value(1 - 2), upper_limit.value(10 + 1)],
                    [lower_limit.value(1), upper_limit.value(10)],
                    [lower_limit.value(1), upper_limit.value(10 + 2)],
                ],
                    max_num_lines_from_iter=10,
                    expected_output_lines=_from_to(1, 10),
                ) +
                model_w_10_elems.equivalent_cases__n([
                    [lower_limit.value(- 2), upper_limit.value(0)],
                    [lower_limit.value(5), upper_limit.value(3)],
                ],
                    max_num_lines_from_iter=0,
                    expected_output_lines=[],
                )
        )


class TestLineNumAndContents(unittest.TestCase):
    def test_conjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        upper_limit = IntSymbol('upper_limit')
        arguments = tr.filter_lm__within_parens(
            arg_rend.conjunction([
                lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                lm_arg.LineNum2(
                    im_args.comparison(
                        comparators.LTE,
                        SymbolReferenceWReferenceSyntax(upper_limit.name)
                    )),
            ])
        )
        model_and_args = ModelAndArguments(model, arguments)
        # ACT & ASSET #
        tr.check_cases__named(
            self,
            [
                model_and_args.case__n(
                    [upper_limit.value(-3)],
                    max_num_lines_from_iter=0,
                    expected_output_lines=[],
                ),
                model_and_args.case__n(
                    [upper_limit.value(2)],
                    max_num_lines_from_iter=2,
                    expected_output_lines=[2],
                ),
                model_and_args.case__n(
                    [upper_limit.value(10)],
                    max_num_lines_from_iter=3,
                    expected_output_lines=[2],
                ),
            ],
        )

    def test_disjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        num_model_elements = len(model)
        upper_limit = IntSymbol('upper_limit')
        arguments = tr.filter_lm__within_parens(
            arg_rend.disjunction([
                lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                lm_arg.LineNum2(
                    im_args.comparison(
                        comparators.LTE,
                        SymbolReferenceWReferenceSyntax(upper_limit.name)
                    )),
            ])
        )
        model_and_args = ModelAndArguments(model, arguments)
        # ACT & ASSET #
        tr.check_cases__named(
            self,
            [
                model_and_args.case__n(
                    [upper_limit.value(-3)],
                    max_num_lines_from_iter=num_model_elements,
                    expected_output_lines=[2],
                ),
                model_and_args.case__n(
                    [upper_limit.value(2)],
                    max_num_lines_from_iter=num_model_elements,
                    expected_output_lines=_from_to(1, 2),
                ),
                model_and_args.case__n(
                    [upper_limit.value(10)],
                    max_num_lines_from_iter=num_model_elements,
                    expected_output_lines=_from_to(1, 3),
                ),
            ],
        )

    def test_negation_of_conjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        neg_open_lower_limit = IntSymbol('lower_limit')
        arguments = tr.filter_lm(
            arg_rend.negation(
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                        lm_arg.LineNum2(
                            im_args.comparison(
                                comparators.GT,
                                SymbolReferenceWReferenceSyntax(neg_open_lower_limit.name)
                            )),
                    ]))
            )
        )
        model_and_args = ModelAndArguments(model, arguments)
        # ACT & ASSET #
        tr.check_cases__named(
            self,
            [
                model_and_args.case__n(
                    [neg_open_lower_limit.value(1)],
                    max_num_lines_from_iter=3,
                    expected_output_lines=[1, 3],
                ),
                model_and_args.case__n(
                    [neg_open_lower_limit.value(2)],
                    max_num_lines_from_iter=3,
                    expected_output_lines=[1, 2, 3],
                ),
            ],
        )

    def test_negation_of_disjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        neg_open_lower_limit = IntSymbol('lower_limit')
        arguments = tr.filter_lm(
            arg_rend.negation(
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                        lm_arg.LineNum2(
                            im_args.comparison(
                                comparators.GT,
                                SymbolReferenceWReferenceSyntax(neg_open_lower_limit.name)
                            )),
                    ]))
            )
        )
        model_and_args = ModelAndArguments(model, arguments)
        # ACT & ASSET #
        tr.check_cases__named(
            self,
            [
                model_and_args.case__n(
                    [neg_open_lower_limit.value(1)],
                    max_num_lines_from_iter=3,
                    expected_output_lines=[1],
                ),
                model_and_args.case__n(
                    [neg_open_lower_limit.value(2)],
                    max_num_lines_from_iter=3,
                    expected_output_lines=[1],
                ),
                model_and_args.case__n(
                    [neg_open_lower_limit.value(3)],
                    max_num_lines_from_iter=3,
                    expected_output_lines=[1, 3],
                ),
            ],
        )


class TestContents(unittest.TestCase):
    def test_non_complex(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        arguments = tr.filter_lm(
            lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd')))
        )
        # ACT & ASSET #
        tr.check(
            self,
            Case(
                model,
                arguments,
                [],
                [model[1]],
                len(model)
            ),
        )

    def test_negation(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        arguments = tr.filter_lm(
            arg_rend.negation(
                lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd')))
            )
        )
        # ACT & ASSET #
        tr.check(
            self,
            Case(
                model,
                arguments,
                [],
                [model[0], model[2]],
                len(model)
            ),
        )

    def test_conjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        arguments = tr.filter_lm__within_parens(
            arg_rend.conjunction([
                lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                lm_arg.Contents(sm_args.Equals(FileOrString.of_string('3rd'))),
            ])
        )
        # ACT & ASSET #
        tr.check(
            self,
            Case(
                model,
                arguments,
                [],
                [],
                len(model)
            ),
        )

    def test_disjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        arguments = tr.filter_lm__within_parens(
            arg_rend.disjunction([
                lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                lm_arg.Contents(sm_args.Equals(FileOrString.of_string('3rd'))),
            ])
        )
        # ACT & ASSET #
        tr.check(
            self,
            Case(
                model,
                arguments,
                [],
                [model[1], model[2]],
                len(model)
            ),
        )

    def test_negation_of_conjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        arguments = tr.filter_lm(
            arg_rend.negation(
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                        lm_arg.Contents(sm_args.Equals(FileOrString.of_string('3rd'))),
                    ])
                ))
        )
        # ACT & ASSET #
        tr.check(
            self,
            Case(
                model,
                arguments,
                [],
                model,
                len(model)
            ),
        )

    def test_negation_of_disjunction(self):
        # ARRANGE #
        model = ['1st\n', '2nd\n', '3rd\n', ]
        arguments = tr.filter_lm(
            arg_rend.negation(
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        lm_arg.Contents(sm_args.Equals(FileOrString.of_string('2nd'))),
                        lm_arg.Contents(sm_args.Equals(FileOrString.of_string('3rd'))),
                    ])
                ))
        )
        # ACT & ASSET #
        tr.check(
            self,
            Case(
                model,
                arguments,
                [],
                [model[0]],
                len(model)
            ),
        )


def _cases_for_lower_limit(model_w_10_elems: ModelAndArguments, lower_limit: IntSymbol):
    return (
            [
                model_w_10_elems.case__n(
                    [lower_limit.value(5)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=_from_to(5, 10),
                ),
                model_w_10_elems.case__n(
                    [lower_limit.value(10)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=[10],
                ),
                model_w_10_elems.case__n(
                    [lower_limit.value(10 + 1)],
                    max_num_lines_from_iter=10,
                    expected_output_lines=[],
                ),
            ] +
            model_w_10_elems.equivalent_cases__n([
                [lower_limit.value(-2)],
                [lower_limit.value(1)],
            ],
                max_num_lines_from_iter=10,
                expected_output_lines=_from_to(1, 10),
            )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
