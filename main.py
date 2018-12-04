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

    payload = json.loads(base64.b64decode(data['data']).decode('utf-8'))

    try:
        validate(payload, JSON_SCHEMA)
    except ValidationError as e:
        m = 'Invalid JSON - {0}'.format(e.message)
        logging.error(m)
        sys.exit(1)

    switch = payload['switch']
    target = payload['target']

    compute = googleapiclient.discovery.build('compute', 'v1')
    switcher = Switcher(compute, PROJECT)

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
        filter = self.__create_filter(self.ON, target)

        instances = self.__list_instances(filter)

        for instance in instances:
            self.compute.instances().start(
                project=self.project, zone=self.__get_value_from_url_resource(instance['zone']), instance=instance['name']).execute()

    def off(self, target):
        filter = self.__create_filter(self.OFF, target)

        instances = self.__list_instances(filter)

        for instance in instances:
            self.compute.instances().stop(
                project=self.project, zone=self.__get_value_from_url_resource(instance['zone']), instance=instance['name']).execute()

    def __list_instances(self, filter):
        zones = self.__list_zones()

        items = []
        for zone in zones:
            result = self.compute.instances().list(
                project=self.project, zone=zone['name'], filter=filter).execute()

            if 'items' in result:
                items.extend(result['items'])

        return items

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

    def __get_value_from_url_resource(self, url):
        values = url.split('/')
        return values[len(values)-1]
