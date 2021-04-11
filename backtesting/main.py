import orjson
import os
from flask import Flask
from flask_cors import CORS
from common import get_date_range_trend


app = Flask(__name__)
CORS(app, resources=r'/*')


@app.route('/backtesting/date/<begin>/<end>')
def echarts(begin, end):
    begin = begin.split('T')[0]
    end = end.split('T')[0]

    data_dir = '/Users/bishop/project/allsense/okex/trend_data/'
    files = get_date_range_trend(begin, end, data_dir)

    datas = []
    for f in files:
        with open(os.path.join(data_dir, f), encoding='utf-8') as fd:
            datas.extend([line.strip().split() for line in fd])

    return orjson.dumps(datas).decode('utf-8')

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5926)