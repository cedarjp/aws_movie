# ec2 cron
data "aws_iam_policy_document" "ec2_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ec2_role_policy" {
  statement {
    actions = [
      "s3:*",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      # AmazonSSMFullAccess
      "cloudwatch:PutMetricData",
      "ds:CreateComputer",
      "ds:DescribeDirectories",
      "ec2:DescribeInstanceStatus",
      "logs:*",
      "ssm:*",
      "ec2messages:*",
      "elastictranscoder:*",
      "iam:ListRoles",
      "sns:ListTopics",
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel"
    ]

    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_role" "ec2" {
  name               = "${var.name}-EC2Role"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.ec2_role.json
}

resource "aws_iam_role_policy" "ec2" {
  role   = aws_iam_role.ec2.id
  name   = "${var.name}-EC2RolePolicy"
  policy = data.aws_iam_policy_document.ec2_role_policy.json
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.name}-EC2InstanceProfile"
  role = aws_iam_role.ec2.name
}

# rds
data "aws_iam_policy_document" "rds" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["monitoring.rds.amazonaws.com"]
    }

    effect = "Allow"
  }
}

resource "aws_iam_role" "rds" {
  name = "${var.db_name}_rds_monitoring"
  path = "/"

  assume_role_policy = data.aws_iam_policy_document.rds.json
}

resource "aws_iam_role_policy_attachment" "monitoring" {
  role       = aws_iam_role.rds.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# lambda_function
data "aws_iam_policy_document" "lambda_function_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_function_role_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "elastictranscoder:Read*",
      "elastictranscoder:List*",
      "elastictranscoder:*Job",
      "elastictranscoder:*Preset",
      "s3:ListAllMyBuckets",
      "s3:ListBucket",
      "s3:ListObjects",
      "s3:DeleteObject",
      "iam:ListRoles",
      "sns:ListTopics"
    ]

    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_role" "lambda_funciton" {
  name               = "${var.name}-LambdaFunctionRole"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.lambda_function_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_funciton_ssm_attach" {
  role       = aws_iam_role.lambda_funciton.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}

resource "aws_iam_role_policy" "lambda_funciton" {
  role   = aws_iam_role.lambda_funciton.id
  policy = data.aws_iam_policy_document.lambda_function_role_policy.json
}

# transcoder
data "aws_iam_policy_document" "transcoder_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["elastictranscoder.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "transcoder_role_policy" {
  statement {
    actions = [
      "s3:Put*",
      "s3:ListBucket",
      "s3:*MultipartUpload*",
      "s3:Get*",
      "s3:*Delete*",
      "s3:*Policy*",
      "sns:Publish",
      "sns:*Remove*",
      "sns:*Delete*",
      "sns:*Permission*"
    ]

    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_role" "transcoder" {
  name               = "${var.name}-TranscoderRole"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.transcoder_role.json
}

resource "aws_iam_role_policy" "transcoder" {
  role   = aws_iam_role.transcoder.id
  policy = data.aws_iam_policy_document.transcoder_role_policy.json
}

# ssm
data "aws_iam_policy_document" "ssm_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ssm_attach" {
  role       = aws_iam_role.ssm.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
}


resource "aws_iam_role" "ssm" {
  name               = "${var.name}-SSMRole"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.ssm_role.json
}
