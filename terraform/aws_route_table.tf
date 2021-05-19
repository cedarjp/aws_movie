resource "aws_route_table" "rtb" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = var.rt_cidr_blok
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = var.name
  }
}

resource "aws_main_route_table_association" "rtb" {
  vpc_id         = aws_vpc.vpc.id
  route_table_id = aws_route_table.rtb.id
}
