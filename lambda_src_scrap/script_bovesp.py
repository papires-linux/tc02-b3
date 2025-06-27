## @file: script_bovesp.py
# @brief: Script para coletar dados do site da B3 e salvar em um bucket S3
# @details: Este script coleta dados do site da B3, valida as informações coletadas e salva os dados em um bucket S3 no formato Parquet.
# @zip: pip install -r requirements.txt -t && zip lambda_function_payload2.zip .


import json
import base64
import requests
import pandas as pd
from datetime import datetime

url = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/"
bucket_s3_nome = "s3-raw-fiap-bc9e2281"

def retorna_encode_codigo_solicitação():
    params = {
        "language": "pt-br",
        "pageNumber": 1,
        "pageSize": 120,
        "index": "IBOV",
        "segment": "1"
    }

    json_str = json.dumps(params)
    base64_bytes = base64.b64encode(json_str.encode('utf-8'))
    base64_str = base64_bytes.decode('utf-8')
    print(f"Base64 Encoded Request: {base64_str}")
    return base64_str

def retorna_dados_solicitados():
    # Requisição
    response = requests.get(url + retorna_encode_codigo_solicitação())

    # Verifica se a requisição teve sucesso
    if response.status_code == 200:
        # Converte o conteúdo para JSON
        data = response.json()
    else:
        data = []
        
    return data

def validar__theorical_qty(valor_esperado: int, dados: list) -> bool:
    try:
        soma = sum(int(item['theoricalQty'].replace('.', '')) for item in dados if item.get('theoricalQty'))
        return int(soma) == int(valor_esperado)
    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro ao validar theoricalQty: {e}")
        return False

def validar__part(valor_esperado: float, dados: list) -> bool:
    try:
        soma = round(sum(float(i.get('part').replace(',', '.')) for i in dados if i.get('part')), 3)
        return float(soma) == float(valor_esperado)
    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro ao validar theoricalQty: {e}")
        return False

def salvar_arquivo_s3(bucket_s3_nome, header_data, dados_results):
    df = pd.DataFrame(dados_results)

    data = datetime.strptime(header_data, '%d/%m/%y')
    data_formatada = data.strftime('%d/%m/%Y')

    dia = data_formatada.split('/')[0]
    mes = data_formatada.split('/')[1]
    ano =  data_formatada.split('/')[2]

    df['part'] = df['part'].str.replace(',', '.').astype(float)
    df['theoricalQty'] = df['theoricalQty'].str.replace('.', '').astype(int)

    s3_path = f"s3://{bucket_s3_nome}/raw_data/b3_parquet/year={ano}/month={mes}/day={dia}/dados.parquet"

    df.to_parquet(s3_path, index=False, engine='pyarrow')

def salvar_arquivo_csv(header_data, dados_results):
    df = pd.DataFrame(dados_results)
    data = datetime.strptime(header_data, '%d/%m/%y')
    data_formatada = data.strftime('%d/%m/%Y')

    dia = data_formatada.split('/')[0]
    mes = data_formatada.split('/')[1]
    ano =  data_formatada.split('/')[2]

    data_yyyymmdd = f"{ano}{mes}{dia}"

    df.to_parquet(f'dados_{data_yyyymmdd}.parquet', index=False, engine='pyarrow')

# Script para coletar dados do site da B3 e salvar em um bucket S3
def main():
    dados = retorna_dados_solicitados()
    print(dados)
    header_data = dados['header'].get('date') # DD/MM/YY
    float_validar_part = float(dados['header'].get('part').replace('.', '').replace(',','.'))
    int_validar_theoricalQty = int(dados['header'].get('theoricalQty').replace('.', ''))
    dados_results = dados.get('results')

    if validar__theorical_qty(int_validar_theoricalQty, dados_results) and validar__part(float_validar_part, dados_results):
        #salvar_arquivo_s3(bucket_s3_nome, header_data, dados_results)
        salvar_arquivo_csv(header_data, dados_results)
        print("Arquivo salvo com sucesso")
    else:
        print("Não foi possível salvar o arquivo")

if __name__ == "__main__":
    main()
# This script collects data from the B3 website and saves it to an S3 bucket.
# It validates the theorical quantity and part before saving.
