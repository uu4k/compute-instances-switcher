from jsonschema import validate, ValidationError
import json
import base64
import logging
import sys
import os
import googleapiclient.discovery

JSON_SCHEMA = json.load(
    open('./schema.json'))

PROJECT = os.environ.get('GCP_PROJECT')


def switch_compute_instances(data, context):

    if 'data' not in data:
        sys.exit(1)

    payload = json.load(base64.b64decode(data['data']).decode('utf-8'))

    try:
        validate(payload, JSON_SCHEMA)
    except ValidationError as e:
        m = 'Invalid JSON - {0}'.format(e.message)
        logging.error(m)
        sys.exit(1)

    switch = payload['switch']
    target = payload['target']

    compute = googleapiclient.discovery.build('compute', 'v1')
    switcher = new Switcher(compute, PROJECT)

    if switch == switcher.ON:
        switcher.on(target)
    elif switch == switcher.OFF:
        switcher.off(target)


class Switcher:

    ON = 'on'
    OFF = 'off'

    def __init__(self, compute, project):
        self.compute = compute
        self.project = project

    def on(self, target):
        # filter構築
        filter = self.__create_filter(self.ON, target)

        # instances取得
        instances = self.__list_instances(filter)

        # 開始

    def off(self, target):
        # filter構築
        filter = self.__create_filter(self.OFF, target)

        # instances取得
        instances = self.__list_instances(filter)

        # 開始

    def __list_instances(self, filter):
        zones = self.__list_zones()
        for zone in zones:
            result = self.compute.instances().list(
                project=self.project, zone=zone['name'], filter=filter).execute()

        return result['items'] if 'items' in result else []

    def __list_zones(self):
        result = self.compute.zones().list(project=self.project).execute()
        return result['items'] if 'items' in result else []

    def __create_filter(self, switch, target):

        filter = 'name:' + target
        if switch == self.ON:
            filter += ' status!=running'
        elif switch == self.OFF:
            filter += ' status=running'

        return filter
