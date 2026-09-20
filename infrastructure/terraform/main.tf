terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "meteor_data_lake" {
  bucket = "meteor-data-lake-397781772486"
}

resource "aws_iam_role" "meteor_lambda_role" {
  name = "meteor-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_lambda_function" "meteor_hello" {
  function_name = "meteor-hello"
  role          = aws_iam_role.meteor_lambda_role.arn
  handler       = "hello_meteor.handler"
  runtime       = "python3.12"
  filename      = "${path.module}/../../lambda_functions/hello_meteor.zip"
}