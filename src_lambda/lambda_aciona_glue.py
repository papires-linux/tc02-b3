import json
import boto3
import os

def lambda_handler(event, context):
    glue = boto3.client('glue')
    job_name = os.environ['GLUE_JOB_NAME']

    print("Evento do S3 recebido:")
    print(json.dumps(event, indent=2))

    try:
        response = glue.start_job_run(JobName=job_name)
        print(f"Glue Job iniciado com JobRunId: {response['JobRunId']}")
        return {
            'statusCode': 200,
            'body': json.dumps('Glue Job iniciado com sucesso!')
        }
    except Exception as e:
        print(f"Erro ao iniciar Glue Job: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Erro ao iniciar Glue Job.')
        }