terraform {
  required_version = ">= 0.11.0"

  backend "s3" {
    bucket         = "movie-app-tfstate-bucket"
    key            = "movie.tfstate.aws"
    region         = "ap-northeast-1"
    dynamodb_table = "movie-lock"
    profile        = "movie"
  }
}

provider "aws" {
  region  = "ap-northeast-1"
  profile = "movie"
}

data "aws_caller_identity" "self" {}
