resource "aws_eip" "web" {
  instance = aws_instance.web[0].id
  vpc = true
}
