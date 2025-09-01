
module "lambda_service" {
  source = "./modules/lambda_service"

  project_name            = var.project_name
  environment             = var.environment
  lambda_function_name    = var.lambda_function_name
  lambda_handler          = var.lambda_handler
  runtime                 = var.runtime
  sqs_queue_name          = var.sqs_queue_name
  batch_size              = var.batch_size
  s3_bucket_name          = var.s3_bucket_name
  glue_job_name           = var.glue_job_name
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}