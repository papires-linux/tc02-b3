output "bucket_name" {
  description = "Nome final do bucket S3 criado"
  value       = aws_s3_bucket.bucket_csv_bolsa.bucket
}

output "lambda_function_name" {
  description = "Nome da função Lambda"
  value       = aws_lambda_function.processa_arquivo.function_name
}

output "lambda_function_arn" {
  description = "ARN da função Lambda"
  value       = aws_lambda_function.processa_arquivo.arn
}

output "s3_bucket_arn" {
  description = "ARN do bucket S3"
  value       = aws_s3_bucket.bucket_csv_bolsa.arn
}

output "lambda_invoke_permission_statement_id" {
  description = "ID da política de permissão da Lambda para ser invocada pelo S3"
  value       = aws_lambda_permission.allow_s3.statement_id
}
