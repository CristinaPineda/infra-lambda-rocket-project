variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "environment" {
  description = "The deployment environment (dev, prod, etc.)."
  type        = string
}

variable "aws_region" {
  description = "The AWS region for the deployment."
  type        = string
  default     = "sa-east-1"
}

variable "lambda_function_name" {
  description = "The name of the Lambda function."
  type        = string
}

variable "lambda_handler" {
  description = "The handler function name."
  type        = string
  default     = "lambda_function.handler"
}

variable "runtime" {
  description = "The Lambda runtime."
  type        = string
  default     = "python3.9"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for idempotency."
  type        = string
}