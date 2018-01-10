import csv
import re

output = []
file = 'log_insurance_healthgrad_1.csv'
with open(file, 'r') as lines:
    spamreader = csv.reader(lines)
    for line in spamreader:
        if 'ERROR' in line[1]:
            text = line[2]
            t = re.findall(r'<GET (.+)?>', text)
            output = output + t
print(output)