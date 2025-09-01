resource "aws_s3_bucket" "idempotency_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}