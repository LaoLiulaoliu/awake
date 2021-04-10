import orjson
import os
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/backtesting/date/<begin>/<end>')
def echarts(begin, end):
    begin = begin.split('T')[0]
    end = end.split('T')[0]

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

    datas = []
    for f in files[start:stop + 1]:
        with open(os.path.join(data_dir, f), encoding='utf-8') as fd:
            datas.extend([line.strip().split() for line in fd])

    return orjson.dumps(datas).decode('utf-8')

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5926)