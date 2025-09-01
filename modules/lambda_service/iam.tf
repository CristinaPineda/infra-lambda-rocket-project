# Data source para obter o ID da conta AWS
# Usado para construir os ARNs das políticas de forma segura
data "aws_caller_identity" "current" {}

# IAM Role de execução para a função Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.lambda_function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Política de permissão para escrever logs no CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Política de permissões para S3 (ler/escrever IDs de mensagens)
resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "${var.lambda_function_name}-s3-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
}

# Política de permissões para acionar o AWS Glue
resource "aws_iam_role_policy" "lambda_glue_policy" {
  name = "${var.lambda_function_name}-glue-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "glue:StartJobRun"
        Effect = "Allow"
        Resource = "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:job/${var.glue_job_name}"
      }
    ]
  })
}

# Política de permissões para a Lambda ler da fila SQS
resource "aws_iam_role_policy" "lambda_sqs_policy" {
  name = "${var.lambda_function_name}-sqs-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Effect = "Allow"
        Resource = "arn:aws:sqs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${var.sqs_queue_name}"
      }
    ]
  })
}