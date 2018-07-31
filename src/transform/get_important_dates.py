from glob import glob
import json
import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, CSV_DIR

def get_important_dates():
    keys = ['School', 'Early Decision 1', 'Application Fee', 'Early Decision 2', 'Regular Decision']
    result = [keys]
    important_dates_json_files = glob(os.path.join(JSON_DIR, 'school_*_important_dates.json'))
    for filename in important_dates_json_files:
        tokens = os.path.basename(filename).split('_')
        assert len(tokens) == 4, 'Invalid filename {}'.format(filename)
        school_name = tokens[1]
        with open(filename, 'rb') as fp:
            data = json.load(fp)
            if not data:
                print 'Bad school data: {}'.format(school_name)
            row = [school_name]
            for k in keys[1:]:
                row.append(data.get(k, 'N/A'))
        result.append(row)
    with open(os.path.join(CSV_DIR, 'important_dates.csv'), 'wb') as fp:
        csv_writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in result:
            csv_writer.writerow(row)


if __name__ == '__main__':
    get_important_dates()
