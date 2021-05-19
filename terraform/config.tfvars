name = "movie-app"
region = "ap-northeast-1"
public_key = "movie.id_rsa.pub"

# ec2 instance
instance_num = 1
instance_type = "t2.micro"
//image_id = "ami-f3f8098c"

# vpc
vpc_cidr_block = "10.0.0.0/16"
vpc_dns_hostnames = "true"
vpc_dns_support = "true"
vpc_instance_tenancy = "default"

# subnet
subnet_cidrs = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
subnet_zones = ["ap-northeast-1a", "ap-northeast-1c", "ap-northeast-1d"]

# route_table
rt_cidr_blok = "0.0.0.0/0"

# alb
alb_idle_timeout = 600
alb_internal = "false"
alb_deletion_protection = "false"
alb_log_s3_bucket_name = "alb-bucket"

# rds
db_instance_type = "db.t2.micro"
db_username = "movie"
db_name = "movie"
db_engine = "mysql"
db_engine_version = "5.7.21"
db_family = "mysql5.7"
db_allocated_storage = 20
db_storage_type = "gp2"
db_port = 3306
db_multi_az = "false"
db_backup_retention = 7
db_monitoring_interval = 60
