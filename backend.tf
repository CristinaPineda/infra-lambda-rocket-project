terraform {  
backend "s3" {
    bucket = "rocket-project-statefiles"
    key    = "lambda-service/terraform.tfstate"
    region = "sa-east-1"
  }
}