import os
from .common import get_date_range_trend

class FakeTrend(object):
    def __init__(self, begin, end, data_dir=None):
        self.data_dir = '/Users/bishop/project/allsense/okex/trend_data/' if data_dir is None else data_dir
        self.files = get_date_range_trend(begin, end, data_dir)

    def iterator(self, reverse=False):
        i = 0
        for f in self.files:
            with open(os.path.join(self.data_dir, f), encoding='utf-8') as fd:
                for line in fd:
                    yield i, line.strip().split()
                    i += 1
        