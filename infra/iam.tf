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

# 1. Política de permissão para escrever logs no CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_execution_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# 2. Política de permissões para S3 (para ler/escrever IDs de mensagens)
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
        # Permite acesso apenas ao bucket específico e seus objetos
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
}

# 3. Política de permissões para acionar o AWS Glue
resource "aws_iam_role_policy" "lambda_glue_policy" {
  name = "${var.lambda_function_name}-glue-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "glue:StartJobRun"
        ]
        Effect = "Allow"
        # Permite iniciar jobs específicos do Glue
        Resource = "arn:aws:glue:*:*:job/*"
      }
    ]
  })
}

# 4. Política para permitir a adição de Tags à Lambda (necessário para o Terraform)
resource "aws_iam_role_policy" "lambda_tag_policy" {
  name = "${var.lambda_function_name}-tag-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "lambda:TagResource"
        Effect = "Allow"
        Resource = "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${var.lambda_function_name}"
      }
    ]
  })
}