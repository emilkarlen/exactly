from exactly_lib.util.command_line_syntax.elements import argument2 as argument
from exactly_lib.util.textformat.structure import structures as docs


class ProgramDocumentationRenderer:
    def __init__(self):
        self.cmd_line_syntax_renderer = CommandLineSyntaxRenderer()

    def apply(self, command_line: argument.CommandLine) -> docs.SectionContents:
        return docs.SectionContents([docs.para(self.cmd_line_syntax_renderer.apply(command_line))], [])


class CommandLineSyntaxRenderer:
    def __init__(self):
        self.arg_usage_renderer = _ArgumentUsageOnCommandLineRenderer()

    def apply(self, command_line: argument.CommandLine) -> docs.Text:
        components = [command_line.program_name] + list(map(self.arg_usage_renderer, command_line.argument_usages))
        return docs.text(' '.join(components))


class _ArgumentUsageOnCommandLineRenderer(argument.ArgumentUsageVisitor):
    CHOICE_SEPARATOR = '|'

    def __init__(self):
        self._arg_renderer = _ArgumentOnCommandLineRenderer()

    def visit_single(self, x: argument.Single) -> str:
        return self._multiplicity(self._arg_renderer.visit(x.argument),
                                  x.multiplicity)

    def visit_choice(self, x: argument.Choice) -> str:
        arg_str = self.CHOICE_SEPARATOR.join(map(self._arg_renderer, x.arguments))
        return self._multiplicity(arg_str, x.multiplicity)

    def _multiplicity(self, arg_str: str, multiplicity: argument.Multiplicity) -> str:
        return arg_str if multiplicity is argument.Multiplicity.MANDATORY else '[' + arg_str + ']'


class _ArgumentOnCommandLineRenderer(argument.ArgumentVisitor):
    LONG_OPTION_PREFIX = '--'
    SHORT_OPTION_PREFIX = '-'

    def visit_constant(self, x: argument.Constant) -> str:
        return x.name

    def visit_named(self, x: argument.Named) -> str:
        return self._value_element(x.element)

    def visit_option(self, x: argument.Option) -> str:
        ret_val = ''
        if x.long_name:
            ret_val = self.LONG_OPTION_PREFIX + x.long_name
        else:
            ret_val = self.SHORT_OPTION_PREFIX + x.short_name
        if x.element:
            return ret_val + ' ' + self._value_element(x.element)
        else:
            return ret_val

    def _value_element(self, x: argument.ArgumentValueElement) -> str:
        if x.is_str:
            return x.str_value
        else:
            return x.syntax_element_value.name
