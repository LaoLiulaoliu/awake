import os


def get_date_range_trend(begin, end, data_dir=None):
    if data_dir is None:
        data_dir = '/Users/bishop/project/allsense/okex/trend_data/'
    files = os.listdir(data_dir)
    files.sort()

    start, stop = 0, len(files)
    for i, fname in enumerate(files):
        if begin in fname:
            start = i
        elif end in fname:
            stop = i
            break
    return files[start:stop + 1]
