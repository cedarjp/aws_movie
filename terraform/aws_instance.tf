data "aws_ami" "amazon" {
  most_recent = true
  owners = ["amazon"]

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "name"
    values = ["amzn-ami-hvm-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "block-device-mapping.volume-type"
    values = ["gp2"]
  }
}

data "template_file" "user_data_web" {
  template = file("${path.module}/templates/user_data_web.tpl")
  vars = {
  }
}

resource "aws_instance" "web" {
  count                       = var.instance_num
  ami                         = data.aws_ami.amazon.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.key.key_name
  subnet_id                   = element(aws_subnet.main.*.id, count.index%length(aws_subnet.main))
  vpc_security_group_ids      = [aws_security_group.sg.id]
  user_data                   = data.template_file.user_data_web.rendered
  associate_public_ip_address = "true"
  iam_instance_profile        = aws_iam_instance_profile.ec2.name

  credit_specification {
    cpu_credits = "standard"
  }

  tags = {
    Name = "${var.name}-${format("web%02d", count.index + 1)}"
    Role = "Web"
  }
}
