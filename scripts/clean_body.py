import csv
import re
import sys
import __future__

if __name__ == "__main__":
    csv_writer = csv.writer(sys.stdout)

    first = True
    for line in csv.reader(sys.stdin):
        if first:
            first = False
            continue
        if line[1].startswith("File:") or line[1].startswith("Category:"):
            continue
        line[1] = unicode(line[1], "utf-8")

        line[2] = re.sub(r'</?a[^>]*>', r'', unicode(line[2], "utf-8"))
        line[2] = re.sub(r'%0A', r'\n', line[2])
        line[2] = re.sub(r'%09', r'\t', line[2])

        # Remove everything past the first section
        line[2] = re.sub(r'=.*', r'', line[2])

        m = re.match(r'(\W*(\w+\W+){150})', line[2])
        if m:
            line[2] = m.group(1) + "..."

        line[2] = re.sub(r'\n', r'\\n', line[2])

        line[1] = line[1].encode("utf-8")
        line[2] = line[2].encode("utf-8")
            
        csv_writer.writerow(line)
            

