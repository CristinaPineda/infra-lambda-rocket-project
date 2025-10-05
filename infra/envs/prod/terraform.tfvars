#Variaveis da fila SQS
sqs_queue_name          = "rocket-project-prod-sqs-queue"

#Variaveis da função Lambda
lambda_function_name    = "rocket-project-prod-lambda"
lambda_handler          = "lambda_function.handler"
runtime                 = "python3.9"
batch_size              = 1

#Variaveis do projeto
project_name            = "rocket-project"
environment             = "prod"
aws_region              = "sa-east-1"

#Variaveis do bucket S3 e Glue
s3_bucket_name          = "rocket-project-prod-bucket-idempotency"
aws_statefile_s3_bucket = "rocket-project-statefiles"
aws_lock_dynamodb_table = "rocket-projec-terraform-lock"
data_output_bucket_name = "rocket-project-prod-spec-data-bucket"
glue_job_name           = "rocket-project-prod-processing-job"