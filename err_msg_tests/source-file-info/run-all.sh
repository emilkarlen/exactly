function hdr
{
    echo '################################'
}

hdr
xly instruction-error-in-stand-alone-case.case
hdr
xly syntax-error-in-stand-alone-case.case
hdr
xly --suite syntax-error-of-case-instruction-in-suite.suite empty.case
hdr
xly --suite instruction-error-of-case-instruction-in-suite.suite empty.case
hdr
xly sym-def-should-show-src-file-of-def/sub1/the.case
