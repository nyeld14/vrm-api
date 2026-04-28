import json
import boto3
import psycopg2
import psycopg2.extras
from django.conf import settings


def get_aurora_connection():
    client = boto3.client(
        'secretsmanager',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    secret = json.loads(
        client.get_secret_value(SecretId=settings.VRM_DB_SECRET_NAME)['SecretString']
    )
    return psycopg2.connect(
        host=secret['host'],
        port=secret.get('port', 5432),
        dbname=secret.get('dbname', 'vrm'),
        user=secret['username'],
        password=secret['password'],
        connect_timeout=10,
        sslmode='prefer',
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
