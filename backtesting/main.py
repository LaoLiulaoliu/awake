import orjson
import os
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/backtesting')
def echarts():
    data_dir = '/mnt/e/trend/test'
    files = os.listdir(data_dir)
    files.sort()

    datas = []
    for f in files:
        with open(os.path.join(data_dir, f), encoding='utf-8') as fd:
            datas.extend([line.strip().split() for line in fd])

    return orjson.dumps(datas).decode('utf-8')

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5926)