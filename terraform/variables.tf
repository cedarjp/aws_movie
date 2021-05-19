variable "name" {}
//variable "domain_name" {}
variable "region" {}
//variable "image_id" {}
variable "instance_type" {}
variable "public_key" {}

# instance
variable "instance_num" {}

# vpc
variable "vpc_cidr_block" {}
variable "vpc_dns_hostnames" {}
variable "vpc_dns_support" {}
variable "vpc_instance_tenancy" {}

# subnet
variable "subnet_cidrs" { type = list }
variable "subnet_zones" { type = list }

# route_table
variable "rt_cidr_blok" {}

# alb
variable "alb_idle_timeout" {}
variable "alb_internal" {}
variable "alb_deletion_protection" {}
variable "alb_log_s3_bucket_name" {}

# rds
variable "db_instance_type" {}
variable "db_username" {}
variable "db_name" {}
variable "db_engine" {}
variable "db_engine_version" {}
variable "db_family" {}
variable "db_allocated_storage" {}
variable "db_storage_type" {}
variable "db_port" {}
variable "db_multi_az" {}
variable "db_backup_retention" {}
variable "db_monitoring_interval" {}
