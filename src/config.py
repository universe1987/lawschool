import os


PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PACKAGE_DIR, 'data')
HTML_DIR = os.path.join(DATA_DIR, 'html')
JSON_DIR = os.path.join(DATA_DIR, 'json')
CSV_DIR = os.path.join(DATA_DIR, 'csv')
ENTRY_DIR = os.path.join(DATA_DIR, 'entry')
CLEAN_DIR = os.path.join(DATA_DIR, 'clean')

for folder in [DATA_DIR, HTML_DIR, JSON_DIR, CSV_DIR, ENTRY_DIR]:
    if not os.path.exists(folder):
        os.mkdir(folder)
