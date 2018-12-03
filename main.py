from jsonschema import validate, ValidationError
import json
import base64
import logging
import sys
import googleapiclient.discovery

JSON_SCHEMA = json.load(
     open('./schema.json'))
def switch_compute_instances(data, context):

    if 'data' not in data:
        exit

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

    instances = list_instances(compute)

    # 同プロジェクトのインスタンスリスト取得

    # targetの正規表現とマッチするかチェック

    # マッチした場合はon/offに応じて起動・停止

def list_instances(compute):
    result = compute.instances().list().execute()
    return result['items'] if 'items' in result else None
