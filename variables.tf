
variable "sqs_queue_arn" {
  description = "The ARN of the SQS queue."
  type        = string
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

variable "batch_size" {
  description = "The number of messages to batch from SQS."
  type        = number
  default     = 2
}

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

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for idempotency."
  type        = string
}

variable "aws_statefile_s3_bucket" {
  description = "The S3 bucket to store Terraform state files."
  type        = string
}

variable "aws_lock_dynamodb_table" {
  description = "The DynamoDB table for Terraform state locking."
  type        = string
}

variable "glue_job_name" {
  description = "The name of the Glue job."
  type        = string
}

variable "data_output_bucket_name" {
  description = "The name of the S3 bucket for Glue job output."
  type        = string
}
