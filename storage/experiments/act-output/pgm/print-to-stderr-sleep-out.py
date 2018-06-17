import sys
import time

sys.stderr.write('output on stderr\n')
sys.stderr.write('output on stderr again\n')
sys.stderr.flush()

sys.stdout.write('output on stdout 1\n')
sys.stdout.flush()

time.sleep(10)

sys.stdout.write('output on stdout\n')
