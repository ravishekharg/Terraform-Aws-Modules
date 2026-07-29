variable "identifier" {
  type        = string
  description = "Unique identifier used for the RDS instance and related resources (subnet group, security group)"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where the RDS instance and its security group will be created"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs to place the RDS instance in (used to build the DB subnet group)"
}

variable "allowed_cidr_blocks" {
  type        = list(string)
  description = "CIDR blocks allowed to reach the database port via the instance's security group"
}

variable "engine" {
  type        = string
  default     = "mysql"
  description = "Database engine to use (e.g. mysql, postgres)"
}

variable "engine_version" {
  type        = string
  default     = "8.0"
  description = "Engine version for the database instance"
}

variable "instance_class" {
  type        = string
  default     = "db.t3.micro"
  description = "RDS instance class (e.g. db.t3.micro)"
}

variable "allocated_storage" {
  type        = number
  default     = 20
  description = "Allocated storage size in GB for the RDS instance"
}

variable "database_name" {
  type        = string
  description = "Name of the initial database to create"
}

variable "username" {
  type        = string
  description = "Master username for the database"
}

variable "password" {
  type        = string
  sensitive   = true
  description = "Master password for the database. Do not hardcode in tfvars; source from a secrets manager"
}

variable "port" {
  type        = number
  default     = 3306
  description = "Port the database listens on"
}

variable "multi_az" {
  type        = bool
  default     = false
  description = "Whether to enable Multi-AZ deployment for high availability"
}

variable "backup_retention_days" {
  type        = number
  default     = 7
  description = "Number of days to retain automated backups"
}

variable "deletion_protection" {
  type        = bool
  default     = true
  description = "Whether to enable deletion protection on the RDS instance. Defaults to true to prevent accidental deletion in production"
}

variable "skip_final_snapshot" {
  type        = bool
  default     = false
  description = "Whether to skip taking a final snapshot when the instance is destroyed. Defaults to false so a snapshot is taken unless explicitly opted out"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags applied to all resources created by this module"
}
