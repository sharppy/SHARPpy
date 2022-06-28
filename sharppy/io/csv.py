
def loadCSV(csv_file_name):
    csv = []
    csv_file = open(csv_file_name, 'r')
    csv_fields = [ f.lower() for f in csv_file.readline().strip().split(',') ]

    for line in csv_file:
        line_dict = dict( (f, v) for f, v in zip(csv_fields, line.strip().split(',')))
        csv.append(line_dict)

    csv_file.close()
    return csv_fields, csv

if __name__ == '__main__':
    import sys
    fields, csv = loadCSV(sys.argv[1])
    print(fields)
