resource "aws_db_subnet_group" "rds" {
  name        = "${var.name}-db-subnet"
  description = "${var.name} db subnet"
  subnet_ids  = aws_subnet.main.*.id
}

resource "aws_db_parameter_group" "rds" {
  name        = "${var.name}-db-parameter"
  family      = var.db_family
  description = "${var.name} db parameter"

  parameter {
    name         = "character_set_client"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "character_set_server"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "character_set_connection"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "character_set_database"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "character_set_filesystem"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "character_set_results"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "collation_connection"
    value        = "utf8mb4_general_ci"
    apply_method = "immediate"
  }

  parameter {
    name         = "time_zone"
    value        = "Asia/Tokyo"
    apply_method = "immediate"
  }
}

resource "random_string" "password" {
  length           = 16
  special          = false
}

resource "aws_db_instance" "rds" {
  identifier                          = "${var.name}-db"
  allocated_storage                   = var.db_allocated_storage
  storage_type                        = var.db_storage_type
  engine                              = var.db_engine
  engine_version                      = var.db_engine_version
  instance_class                      = var.db_instance_type
  name                                = var.db_name
  username                            = var.db_username
  password                            = random_string.password.result
  port                                = var.db_port
  vpc_security_group_ids              = [aws_security_group.sg.id]
  db_subnet_group_name                = aws_db_subnet_group.rds.name
  parameter_group_name                = aws_db_parameter_group.rds.name
  multi_az                            = var.db_multi_az
  backup_retention_period             = var.db_backup_retention
  final_snapshot_identifier           = "${var.db_name}-final"
  monitoring_role_arn                 = aws_iam_role.rds.arn
  monitoring_interval                 = var.db_monitoring_interval
  iam_database_authentication_enabled = true
}
