import base64
import json
import os

import requests
from flask import Flask
from flask import render_template

app = Flask(__name__)

API_KEY = os.environ.get('ARUKAS_API_KEY')
API_SECRET = os.environ.get('ARUKAS_API_SECRET')


@app.route('/')
def server():
    if not API_KEY or not API_SECRET:
        return "APIKEY／SECRET未设置"

    url = 'https://app.arukas.io/api/containers'
    headers = {
        'authorization': "Basic %s" % base64.b64encode((API_KEY + ":" + API_SECRET).encode()).decode(),
    }
    resp = requests.get(url, headers=headers)
    val = resp.json()
    configures = {

    }
    for container in val['data']:
        attrs = container['attributes']
        if attrs['image_name'].find('ourbest/ss-kcp') == 0:
            for port in attrs['port_mappings'][0]:
                server = port['host']
                server = server[server.find('-') + 1:server.find('.')].replace('-', '.')
                p = port['service_port']
                if port['container_port'] == 8989:
                    configures['ss'] = {
                        "server": server,
                        "server_port": p,
                        "password": "kexueshangwang",
                        "method": "aes-256-cfb"
                    }
                    configures['ss_str'] = json.dumps(configures['ss'])

                elif port['container_port'] == 6688:
                    configures['kcp'] = {
                        "localaddr": ":22222",
                        "remoteaddr": "%s:%s" % (server, p),
                        "key": "chacha", "crypt": "xor",
                        "mode": "fast2", "mtu": 1350, "sndwnd": 512, "rcvwnd": 1024, "datashard": 70,
                        "parityshard": 30, "dscp": 46
                    }

                    configures['kcp_str'] = json.dumps(configures['kcp'])
    return render_template('result.html', config=configures)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
