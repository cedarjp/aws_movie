resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = var.subnet_cidrs[count.index]
  availability_zone       = var.subnet_zones[count.index]
  map_public_ip_on_launch = false
  count                   = length(var.subnet_cidrs)

  tags = {
    Name = var.name
  }
}
