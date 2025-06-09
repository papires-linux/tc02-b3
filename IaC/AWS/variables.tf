variable "bucket_name" {
  description = "Nome do bucket S3"
  type        = string
  default     = "s3-raw-fiap"
}

variable "region" {
  description = "Regiao do ambiente"
  type        = string
  default     = "us-east-1"
}

