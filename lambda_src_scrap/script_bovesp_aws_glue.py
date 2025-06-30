import sys
import json
import base64
import requests
import pandas as pd
from datetime import datetime

from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

#
sys.argv += ['--index_name', 'IBOV']
sys.argv += ['--bucket_name_parquet', 'aws-logs-594530436211-us-east-1']

# Inicializa Glue Context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'index_name','bucket_name_parquet'])
index_b3 = args['index_name']
bucket_s3_nome = args['bucket_name_parquet']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# --- Configuração ---
url = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/"

# --- Funções auxiliares ---
def retorna_encode_codigo_solicitação():
    params = {
        "language": "pt-br",
        "pageNumber": 1,
        "pageSize": 120,
        "index": index_b3,   # <-- usando parâmetro passado pelo job
        "segment": "1"
    }
    json_str = json.dumps(params)
    base64_bytes = base64.b64encode(json_str.encode('utf-8'))
    return base64_bytes.decode('utf-8')

def retorna_dados_solicitados():
    response = requests.get(url + retorna_encode_codigo_solicitação())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na requisição: {response.status_code}")
        return {}

def validar__theorical_qty(valor_esperado: int, dados: list) -> bool:
    try:
        soma = sum(int(item['theoricalQty'].replace('.', '')) for item in dados if item.get('theoricalQty'))
        return int(soma) == int(valor_esperado)
    except Exception as e:
        print(f"Erro ao validar theoricalQty: {e}")
        return False

def validar__part(valor_esperado: float, dados: list) -> bool:
    try:
        soma = round(sum(float(i.get('part').replace(',', '.')) for i in dados if i.get('part')), 3)
        return float(soma) == float(valor_esperado)
    except Exception as e:
        print(f"Erro ao validar part: {e}")
        return False

def salvar_arquivo_s3(header_data, dados_results):
    df = pd.DataFrame(dados_results)
    data = datetime.strptime(header_data, '%d/%m/%y')
    data_formatada = data.strftime('%d/%m/%Y')

    dia, mes, ano = data_formatada.split('/')

    df['part'] = df['part'].str.replace(',', '.').astype(float)
    df['theoricalQty'] = df['theoricalQty'].str.replace('.', '').astype(int)

    s3_path = f"s3://{bucket_s3_nome}/dados_parquet/raw_data/b3_parquet/year={ano}/month={mes}/day={dia}/dados.parquet"
    df.to_parquet(s3_path, index=False, engine='pyarrow')
    print(f"Arquivo salvo em {s3_path}")

# --- Execução principal ---
def main():
    dados = retorna_dados_solicitados()
    if not dados:
        print("Nenhum dado retornado da B3.")
        return

    header_data = dados.get('header', {}).get('date')
    float_validar_part = float(dados['header'].get('part').replace('.', '').replace(',', '.'))
    int_validar_theoricalQty = int(dados['header'].get('theoricalQty').replace('.', ''))
    dados_results = dados.get('results')

    if validar__theorical_qty(int_validar_theoricalQty, dados_results) and validar__part(float_validar_part, dados_results):
        salvar_arquivo_s3(header_data, dados_results)
    else:
        print("Validações falharam, arquivo não será salvo.")

main()
job.commit()
