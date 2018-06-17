import sys
import time

sys.stdout.write('output on stdout 1\n')
sys.stderr.write('output on stderr 1\n')
time.sleep(2)
sys.stdout.write('output on stdout 2\n')
sys.stderr.write('output on stderr 2\n')
