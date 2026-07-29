output "endpoint" {
  value       = aws_db_instance.main.endpoint
  description = "Connection endpoint (host:port) for the RDS instance"
}

output "port" {
  value       = aws_db_instance.main.port
  description = "Port the RDS instance is listening on"
}

output "db_name" {
  value       = aws_db_instance.main.db_name
  description = "Name of the initial database created on the instance"
}

output "instance_id" {
  value       = aws_db_instance.main.identifier
  description = "Identifier of the RDS instance"
}

output "security_group_id" {
  value       = aws_security_group.rds.id
  description = "ID of the security group attached to the RDS instance"
}
