from retrying import retry
import time

def retry_if_error(exception):
    print('sleeped')
    return isinstance(exception, IOError)

@retry(stop_max_attempt_number=3, retry_on_exception=retry_if_error)
def read_file():
    print('begin')
    with open('file', 'r') as f:
        return f.read()


try:
    read_file()
except Exception as e:
    print('e is: ', e)