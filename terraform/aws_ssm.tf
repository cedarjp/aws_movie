resource "aws_ssm_activation" "prediction" {
  name               = "ssm_activation"
  description        = "SSM Role"
  iam_role           = aws_iam_role.ssm.id
  registration_limit = "5"
  depends_on         = [aws_iam_role_policy_attachment.ssm_attach]
}

resource "aws_ssm_association" "prediction" {
  name = aws_ssm_document.prediction.name

  targets {
    key    = "InstanceIds"
    values = aws_instance.web.*.id
  }
}

data "template_file" "aws_ssm_document_prediction" {
  template = file("${path.module}/templates/aws_ssm_document_prediction.json")

  vars = {
  }
}

resource "aws_ssm_document" "prediction" {
  name          = "prediction_document"
  document_type = "Command"

  content = data.template_file.aws_ssm_document_prediction.rendered
}
