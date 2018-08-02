function run # ARG...
{
    echo '################################################################'
    xly $*
}

run instruction-error-in-stand-alone-case.case
run syntax-error-in-stand-alone-case.case
run --suite syntax-error-of-case-instruction-in-suite.suite empty.case
run --suite instruction-error-of-case-instruction-in-suite.suite empty.case
run sym-def-should-show-src-file-of-def/sub1/the.case
run syntax-error-in-included-file.case
run inclusion-of-non-existing-file-in-included-file.case
run suite syntax-error-of-suite-instruction.suite
