variable "bucket_name" {
  description = "Prefixo do nome do bucket S3"
  type        = string
  default     = "s3-raw-fiap"
}

variable "region" {
  description = "Regiao do ambiente"
  type        = string
  default     = "us-east-1"
}


variable "lambda_function_name" {
  default = "processa_arquivo_s3"
}

variable "lambda_function_name_scrap" {
  default = "scrap_to_s3_function"
}


variable "glue_job_name" {
  default = "meu-job-glue"
}

variable "glue_script_path" {
  description = "Caminho no S3 para o script .py do Glue"
  default     = "s3://meu-bucket/scripts/meu_script_etl.py"
}