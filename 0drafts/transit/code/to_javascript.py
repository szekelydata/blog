timings = [ row.strip().split('\t') for row in file('timings.csv') ]

dups = dict()
dup_count = 0

with open('timings.js', 'w') as outf:
    outf.write('var timings = [\n')

    for row in timings:
        line = ','.join(row)
        if not dups.has_key(line):
            outf.write('[ %s ],\n' % line)
            dups[line] = True
        else:
            dup_count += 1

    outf.write('];\n')

print 'Found %d duplicates.' % dup_count