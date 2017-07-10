# -*- coding: utf-8 -*-

import base64
import json
import os

import requests
from flask import Flask, jsonify
from flask import render_template

app = Flask(__name__)

API_KEY = os.environ.get('ARUKAS_API_KEY')
API_SECRET = os.environ.get('ARUKAS_API_SECRET')
PASSWORD = os.environ.get('SS_PASSWORD')

raven_dsn = os.environ.get('RAVEN_DSN')

if raven_dsn:
    from raven.contrib.flask import Sentry

    sentry = Sentry(app, dsn=raven_dsn)


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
    configures = list()
    for container in val['data']:
        config = dict()
        attrs = container['attributes']
        if attrs['image_name'].find('ourbest/ssr-kcp') == 0:
            for port in attrs['port_mappings'][0]:
                server = port['host']
                server = server[server.find('-') + 1:server.find('.')].replace('-', '.')
                p = port['service_port']
                if port['container_port'] == 8989:
                    config['ss'] = {
                        "server": server,
                        "server_port": p,
                        "password": PASSWORD,
                        "method": "aes-256-cfb"
                    }
                    config['ss_str'] = json.dumps(config['ss'])

                elif port['container_port'] == 6688:
                    config['kcp'] = {
                        "localaddr": ":22222",
                        "remoteaddr": "%s:%s" % (server, p),
                        "key": "chacha", "crypt": "xor",
                        "mode": "fast2", "mtu": 1350, "sndwnd": 512, "rcvwnd": 1024, "datashard": 70,
                        "parityshard": 30, "dscp": 46
                    }

                    config['kcp_str'] = json.dumps(config['kcp'])

            configures.append(config)

    return render_template('result.html', configures=configures)


@app.route('/ping')
def ping():
    return jsonify(result='ok')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
