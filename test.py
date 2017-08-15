import os
import csv
root_dir = os.path.abspath(os.path.dirname(__file__))
#print root_dir

files_list = os.listdir('input')
n=0
for f in files_list:
    n=n+1
    print n
    path = 'input/' + f
    ofile = open('output/' + f, "wb")
    writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    with open(path, 'rb') as my_file:
        reader = csv.reader(x.replace('\0', '') for x in my_file)
        for n, row in enumerate(reader):
            line = []
            try:
                uid = row[0]
                first_name = row[1]
                last_name = row[2]
                title = row[3]
                state = row[12]
                line.append(uid)
                line.append(first_name)
                line.append(last_name)
                line.append(title)
                line.append(state)
                writer.writerow(line)
            except:
                pass
        my_file.close()

