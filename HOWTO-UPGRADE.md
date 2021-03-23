Describes how to upgrade test cases to one version from the preceding version.

# [0.15.0]

## Instruction `dir` - Fails if the directory already exists

Make sure the directory do not already exist.

## Type `string`, `list` and `PROGRAM-ARGUMENT` - Reserved words

Surround any plain reserved word with single quotes:

 - `(` -> `'('`
 - `)` -> `')'`
 - `[` -> `'['`
 - `]` -> `']'`
 - `{` -> `'{'`
 - `}` -> `'}'`
 - `:` -> `':'`

## New `RICH-STRING` syntax

Unquoted string constant `:>` must be quoted for

 - Instruction `def` / type  `string`
 - Type `text-source`
 - Syntax element `REGEX`

Unquoted string constant for the form `<<MARKER` must be quoted for syntax element `PROGRAM-ARGUMENT`

## PATH values may not be surrounded by parentheses

Remove any parentheses around PATH values.

# [0.14.0]

## Renaming of types

Replace

    def string-

with

    def text-

Note: This assumes that there is a single space between
`def` and `string-`.

## Instruction `timeout` - moved to the `[setup]` phase

Move

    timeout INTEGER

from the `[conf]` phase to the `[setup]` phase.

## Remove support for Python 3.5

Upgrade Python to a version >= 3.6.
