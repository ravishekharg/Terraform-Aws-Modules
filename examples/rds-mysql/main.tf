module "mysql" {
  source = "../../modules/rds"

  identifier          = "platform-mysql-dev"
  vpc_id              = "vpc-xxxxxxxx"
  subnet_ids          = ["subnet-aaa", "subnet-bbb"]
  allowed_cidr_blocks = ["10.0.0.0/16"]

  database_name = "appdb"
  username      = "admin"
  password      = "change-me-use-secrets-manager"

  instance_class        = "db.t3.micro"
  multi_az              = false
  backup_retention_days = 7
  deletion_protection   = false
  skip_final_snapshot   = true

  tags = { Environment = "dev", ManagedBy = "terraform" }
}

output "mysql_endpoint" { value = module.mysql.endpoint }