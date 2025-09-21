# data sources para recursos que ja existem
data "aws_sqs_queue" "source_queue" {
  name = var.sqs_queue_name
}

data "aws_s3_bucket" "data_output" {
  bucket = var.data_output_bucket_name
}

data "aws_glue_job" "glue_job" {
  name = var.glue_job_name
}

module "lambda_service" {
  source = "./modules/lambda_service"

  project_name             = var.project_name
  environment              = var.environment
  lambda_function_name     = var.lambda_function_name
  lambda_handler           = var.lambda_handler
  runtime                  = var.runtime
  batch_size               = var.batch_size
  aws_statefile_s3_bucket  = var.aws_statefile_s3_bucket
  aws_lock_dynamodb_table  = var.aws_lock_dynamodb_table
  
  sqs_queue_name           = data.aws_sqs_queue.source_queue.name
  sqs_queue_arn            = data.aws_sqs_queue.source_queue.arn
  glue_job_name            = data.aws_glue_job.glue_job.name
  data_output_bucket_name  = data.aws_s3_bucket.data_output.bucket

  s3_bucket_name           = var.s3_bucket_name
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
