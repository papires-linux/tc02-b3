#### - START S3
provider "aws" {
  region = "${var.region}"
}

resource "random_id" "sufixo" {
  byte_length = 4 
}

resource "aws_s3_bucket" "bucket_csv_bolsa" {
  bucket = "${var.bucket_name}-${random_id.sufixo.hex}"
  tags = {
    Name        = "Bucket S3 ${var.bucket_name}"
    Environment = "Dev"
  }
}
### - END S3

### - START LAMBDA
# Função Lambda (código inline ou via zip)
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Effect = "Allow",
      Sid = ""
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_exec" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

### - FUNCAO LAMBDA REQUISITO 1

resource "aws_lambda_function" "scrap_bolsa" {
  function_name = var.lambda_function_name_scrap
  role          = aws_iam_role.lambda_exec_role.arn
  runtime       = "python3.12"
  handler       = "lambda_function.lambda_handler"

  filename      = "../../src_scrap/lambda_function_payload.zip"  # O arquivo compactado com seu código Python

  source_code_hash = filebase64sha256("../../src_lambda/lambda_function_payload.zip")

  depends_on = [aws_iam_role_policy_attachment.lambda_basic_exec]
}

# Permitir que S3 acione a Lambda
resource "aws_lambda_permission" "allow_s3_scrap_bolsa" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scrap_bolsa.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket_csv_bolsa.arn
}

#### - FUNCAO LAMBDA REQUISITO 4
resource "aws_lambda_function" "processa_arquivo" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec_role.arn
  runtime       = "python3.12"
  handler       = "lambda_function.lambda_handler"

  filename      = "../../src_lambda/lambda_function_payload.zip"  # O arquivo compactado com seu código Python

  source_code_hash = filebase64sha256("../../src_lambda/lambda_function_payload.zip")

  depends_on = [aws_iam_role_policy_attachment.lambda_basic_exec]
}

# Permitir que S3 acione a Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processa_arquivo.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket_csv_bolsa.arn
}

# Adicionar trigger no S3
resource "aws_s3_bucket_notification" "s3_to_lambda" {
  bucket = aws_s3_bucket.bucket_csv_bolsa.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.processa_arquivo.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
### - END LAMBDA

### - START GLUE

resource "aws_glue_catalog_database" "glue_db" {
  name = "meu_banco_glue"
}

resource "aws_iam_role" "glue_job_role" {
  name = "glue_job_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "glue.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      },
      {
        "Effect": "Allow",
        "Action": ["s3:GetObject", "s3:ListBucket"],
        "Resource": [
          "arn:aws:s3:::${aws_s3_bucket.bucket_csv_bolsa.bucket}",
          "arn:aws:s3:::${aws_s3_bucket.bucket_csv_bolsa.bucket}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_policy_attach" {
  role       = aws_iam_role.glue_job_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_glue_job" "meu_job" {
  name     = var.glue_job_name
  role_arn = aws_iam_role.glue_job_role.arn

  command {
    name            = "glueetl"
    script_location = var.glue_script_path
    python_version  = "3"
  }

  glue_version     = "4.0"        # ou 3.0 se preferir
  max_retries      = 1
  timeout          = 10           # minutos
  number_of_workers = 2
  worker_type       = "Standard"      # tipos: Standard, G.1X, G.2X

  default_arguments = {
    "--job-language"           = "python"
    "--TempDir"                = "s3://meu-bucket/temp/"
    "--enable-metrics"         = ""
    "--enable-continuous-cloudwatch-log" = "true"
  }

  depends_on = [aws_iam_role_policy_attachment.glue_policy_attach]
}
### - END GLUE