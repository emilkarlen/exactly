import os

output = []

for root, dirs, file_names in os.walk('.'):
    prefix = root + '/'
    if prefix[0:2] == './':
        prefix = prefix[2:]
    for f in file_names:
        output.append(prefix + f)
    for d in dirs:
        output.append(prefix + d + '/')

output.sort()
for l in output:
    print(l)
