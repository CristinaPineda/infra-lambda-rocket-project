output "lambda_function_arn" {
  value = aws_lambda_function.main.arn
}

output "idempotency_bucket_id" {
  value = aws_s3_bucket.idempotency_bucket.id
}