data "template_file" "alb_log_s3_policy" {
  template = file("${path.module}/templates/alb_log_s3_policy.json")

  vars = {
    alb_log_s3_bucket_name = "${var.name}-${var.alb_log_s3_bucket_name}"
    aws_elb_service_account_arn = data.aws_elb_service_account.alb.arn
  }
}

resource "aws_s3_bucket" "alb_log" {
  bucket = "${var.name}-${var.alb_log_s3_bucket_name}"
  acl    = "private"

  policy = data.template_file.alb_log_s3_policy.rendered
}

resource "aws_s3_bucket" "video_upload" {
  bucket = "${var.name}-video-upload"
  acl    = "private"
}

resource "aws_s3_bucket" "video_thumb" {
  bucket = "${var.name}-video-thumb"
  acl    = "private"
}

resource "aws_s3_bucket" "video_stream" {
  bucket = "${var.name}-video-stream"
  acl    = "private"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_notification" "video_upload" {
  bucket = aws_s3_bucket.video_upload.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda.arn
    events              = ["s3:ObjectCreated:Put", "s3:ObjectCreated:CompleteMultipartUpload"]
  }
}

resource "aws_s3_bucket" "video_predict" {
  bucket = "${var.name}-video-predict"
  acl    = "private"
}

