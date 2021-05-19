data "aws_elb_service_account" "alb" {}

resource "aws_alb" "alb" {
  name               = var.name
  idle_timeout       = var.alb_idle_timeout
  internal           = var.alb_internal
  load_balancer_type = "application"
  security_groups    = [aws_security_group.sg-lb.id]
  subnets            = aws_subnet.main.*.id

  enable_deletion_protection = var.alb_deletion_protection

  access_logs {
    bucket  = aws_s3_bucket.alb_log.bucket
    prefix  = "${var.name}-lb"
    enabled = true
  }

  tags = {
    Name = var.name
  }
}

resource "aws_alb_target_group" "alb" {
  count    = var.instance_num
  name     = "${var.name}-tg-${count.index+1}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.vpc.id

  health_check {
    interval            = 5
    path                = "/"
    port                = 80
    protocol            = "HTTP"
    timeout             = 2
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = 200
  }
}

resource "aws_alb_listener" "alb" {
  load_balancer_arn = aws_alb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
//    target_group_arn = element(aws_alb_target_group.alb.*.arn, count.index)
    target_group_arn = element(concat(aws_alb_target_group.alb.*.arn, [""]), 0)
    type             = "forward"
  }
}

resource "aws_lb_target_group_attachment" "alb" {
  count            = var.instance_num
  target_group_arn = element(aws_alb_target_group.alb.*.arn, count.index)
  target_id        = element(aws_instance.web.*.id, count.index)
  port             = 80
}
