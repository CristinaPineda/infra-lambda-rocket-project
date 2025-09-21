data "aws_s3_bucket" "bucket" {
  bucket = var.s3_bucket_name
}

# Data source para empacotar o código da função Lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "infra-lambda-rocket-project/lambda_function"
  output_path = "lambda_function.zip"
}

# Recurso da função Lambda
resource "aws_lambda_function" "main" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = var.lambda_handler
  runtime       = var.runtime

  # O pacote de código é gerado pelo data source 'archive_file'
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }

  environment {
    variables = {
      IDEMPOTENCY_BUCKET_NAME = var.s3_bucket_name
      GLUE_JOB_NAME           = var.glue_job_name
      DATA_BUCKET_OUTPUT      = var.data_output_bucket_name
    }
  }
}


# Conecta a função Lambda à fila SQS
resource "aws_lambda_event_source_mapping" "sqs_mapping" {
  function_name     = aws_lambda_function.main.arn
  event_source_arn  = var.sqs_queue_name
  batch_size        = var.batch_size
  enabled           = true

  depends_on = [
    aws_iam_role_policy.lambda_sqs_policy
  ]
}