OUTPUT = """\
timing 00:01 begin
not a timing line
timing 01:10 preprocessing
not a timing line
timing 02:20 validation
timing 03:30 execution
timing 04:40 end
"""

with open('log.txt', 'w') as f:
    f.write(OUTPUT)
