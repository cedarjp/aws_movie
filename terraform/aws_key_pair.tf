resource "aws_key_pair" "key" {
  key_name = "${var.name}-key"
  public_key = file("${path.module}/${var.public_key}")
}
