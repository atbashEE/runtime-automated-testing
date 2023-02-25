import time

import requests


def wait_until_healthy(url):
    time.sleep(1)
    start_time = time.time()
    result = True
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.2)  # 200 ms wait
        if time.time() - start_time >= 10:
            print("Timeout reached for Health endpoint")
            result = False
            break
    return result


def get_on_endpoint(url):
    return requests.get(url)