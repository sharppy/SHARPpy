import urllib.request as request
from contextlib import closing
import csv

def loadCSV(csv_file_name):
    csv = []
    csv_file = open(csv_file_name, 'r')
    csv_fields = [ f.lower() for f in csv_file.readline().strip().split(',') ]

    for line in csv_file:
        line_dict = dict( (f, v) for f, v in zip(csv_fields, line.strip().split(',')))
        csv.append(line_dict)

    csv_file.close()
    return csv_fields, csv

def loadNUCAPS_CSV(remote_csv):
    csv_dict = []

    # Open the remote csv and define the csv reader object.
    with closing(request.urlopen(remote_csv)) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        csv_file = csv.reader(lines)

        # Assign the headers to a list.
        csv_fields = next(csv_file)

        for line in csv_file:
            line_dict = dict( (f, v) for f, v in zip(csv_fields, line))
            csv_dict.append(line_dict)
    return csv_fields, csv_dict

if __name__ == '__main__':
    import sys
    fields, csv = loadCSV(sys.argv[1])
    print(fields)
