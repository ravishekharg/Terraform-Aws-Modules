# rds

Provisions an RDS instance (MySQL by default) along with a dedicated
security group, a DB subnet group, and an IAM role for enhanced monitoring.

Security/reliability defaults baked into this module:
- `storage_encrypted = true` (always on, not configurable)
- `publicly_accessible = false` (always on, not configurable)
- `deletion_protection` defaults to `true`
- Performance Insights and enhanced monitoring (60s interval) are always enabled
- `error` and `slowquery` logs are exported to CloudWatch
- The instance's security group only allows inbound traffic from
  `var.allowed_cidr_blocks` on `var.port` — there is no public/open default

## Requirements

| Name | Version |
|------|---------|
| Terraform | >= 1.7.0 |
| AWS Provider | ~> 6.0 |

## Usage

See [examples/rds-mysql](../../examples/rds-mysql/) for a complete, runnable
example.

```hcl
module "mysql" {
  source = "../../modules/rds"

  identifier          = "platform-mysql-dev"
  vpc_id              = "vpc-xxxxxxxx"
  subnet_ids          = ["subnet-aaa", "subnet-bbb"]
  allowed_cidr_blocks = ["10.0.0.0/16"]

  database_name = "appdb"
  username      = "admin"
  password      = var.db_password # source from a secrets manager, not a literal

  tags = { Environment = "dev" }
}
```

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `identifier` | `string` | n/a | Unique identifier used for the RDS instance and related resources |
| `vpc_id` | `string` | n/a | ID of the VPC where the RDS instance and its security group will be created |
| `subnet_ids` | `list(string)` | n/a | Subnet IDs to place the RDS instance in |
| `allowed_cidr_blocks` | `list(string)` | n/a | CIDR blocks allowed to reach the database port |
| `engine` | `string` | `"mysql"` | Database engine to use |
| `engine_version` | `string` | `"8.0"` | Engine version for the database instance |
| `instance_class` | `string` | `"db.t3.micro"` | RDS instance class |
| `allocated_storage` | `number` | `20` | Allocated storage size in GB |
| `database_name` | `string` | n/a | Name of the initial database to create |
| `username` | `string` | n/a | Master username for the database |
| `password` | `string` (sensitive) | n/a | Master password; source from a secrets manager |
| `port` | `number` | `3306` | Port the database listens on |
| `multi_az` | `bool` | `false` | Whether to enable Multi-AZ deployment |
| `backup_retention_days` | `number` | `7` | Number of days to retain automated backups |
| `deletion_protection` | `bool` | `true` | Whether to enable deletion protection |
| `skip_final_snapshot` | `bool` | `false` | Whether to skip a final snapshot on destroy |
| `tags` | `map(string)` | `{}` | Common tags applied to all resources created by this module |

## Outputs

| Name | Description |
|------|-------------|
| `endpoint` | Connection endpoint (host:port) for the RDS instance |
| `port` | Port the RDS instance is listening on |
| `db_name` | Name of the initial database created on the instance |
| `instance_id` | Identifier of the RDS instance |
| `security_group_id` | ID of the security group attached to the RDS instance |
