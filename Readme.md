# 02 - TECH CHALLENGE

## Objetivo: 
Fazer 





## README - Coleta e Validação de Dados do IBOV com Salvamento no S3
### Descrição
Este script Python realiza a coleta de dados da carteira diária do índice IBOVESPA (IBOV) através da API pública da B3, valida a consistência dos dados e salva o resultado em um arquivo Parquet organizado por data em um bucket S3.

### Funcionalidades
- Gera a requisição codificada em base64 para a API da B3.
- Faz o download dos dados da carteira diária do índice IBOV.
- Valida a soma dos valores theoricalQty e part conforme esperado no cabeçalho da resposta.
- Converte e salva os dados validados em formato Parquet em uma estrutura de pastas no S3 (ano, mês, dia).
- Utiliza pandas para manipulação e formatação dos dados.

### Dependências
Python 3.6+

### Bibliotecas Python:
requests
pandas
pyarrow (para salvar Parquet)
Configuração do AWS CLI / credenciais para acesso ao bucket S3

### Como usar
Configurar o bucket S3
Atualize a variável bucket_s3 no script com o nome do seu bucket S3.
Executar o script
Basta rodar o script:

```bash
python seu_script.py
```

Se a validação dos dados for bem-sucedida, um arquivo Parquet será salvo no caminho:

```bash 
s3://<bucket_s3>/year=YYYY/month=MM/day=DD/dados.parquet
```

### Estrutura do Código
- retorna_encode_codigo_solicitação(): Monta e codifica em base64 os parâmetros da requisição.
- retorna_dados_solicitados(): Executa a requisição GET e retorna os dados JSON.
- validar__theorical_qty(valor_esperado, dados): Valida se a soma dos theoricalQty está correta.
- validar__part(valor_esperado, dados): Valida se a soma dos part está correta.
- salvar_arquivo_s3(header_data, dados_results): Converte dados para DataFrame, ajusta tipos e salva no S3 em formato Parquet.

### Observações
- A função salvar_arquivo_s3 utiliza o engine pyarrow para salvar arquivos Parquet.
- É necessário garantir as permissões corretas para escrita no bucket S3 configurado.
- Em caso de falha na validação dos dados, o arquivo não será salvo e será exibida uma mensagem de erro.



```bash
terraform apply -target=<recurso>
```


```bash
terraform apply -target=aws_lambda_function.scrap_bolsa
```