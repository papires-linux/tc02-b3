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

#### - END S3