import json
import boto3
#import urllib.parse

glue = boto3.client('glue')
def lambda_handler(event, context):
    try:
        # Nome do job Glue
        nome_job = 'Trusted'

        # Você pode passar argumentos para o Glue Job se quiser
        resposta = glue.start_job_run(
            JobName=nome_job
        )

        print(f"Job Glue iniciado com ID: {resposta['JobRunId']}")
        return {
            'statusCode': 200,
            'body': json.dumps('Glue Job iniciado com sucesso!')
        }

    except Exception as e:
        print(f"Erro ao iniciar o job: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro ao iniciar o job: {str(e)}")
        }
