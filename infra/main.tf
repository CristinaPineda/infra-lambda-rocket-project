provider "aws" {
  region = var.aws_region
}

# Data source para empacotar o código da função Lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "lambda_function"
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
}