output "lambda_function_name" {
  description = "The name of the Lambda function."
  value       = aws_lambda_function.main.function_name
}

output "lambda_function_arn" {
  description = "The ARN of the Lambda function."
  value       = aws_lambda_function.main.arn
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket."
  value       = aws_s3_bucket.s3_bucket_name.bucket
}
