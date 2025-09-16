variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., 'dev', 'prod')."
  type        = string
}

variable "lambda_function_name" {
  description = "The name of the Lambda function."
  type        = string
}

variable "lambda_handler" {
  description = "The Lambda function handler."
  type        = string
  default     = "lambda_function.handler"
}

variable "runtime" {
  description = "The runtime of the Lambda function."
  type        = string
  default     = "python3.9"
}

variable "sqs_queue_name" {
  description = "The name of the SQS queue to connect to."
  type        = string
}

variable "batch_size" {
  description = "The number of messages to batch from SQS."
  type        = number
  default     = 10
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for idempotency keys."
  type        = string
}

variable "glue_job_name" {
  description = "The name of the Glue job to be triggered."
  type        = string
}

variable "aws_region" {
  description = "The AWS region to deploy the resources."
  type        = string
  default     = "sa-east-1"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for idempotency."
  type        = string
}
