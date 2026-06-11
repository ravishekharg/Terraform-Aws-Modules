output "endpoint"        { value = aws_db_instance.main.endpoint }
output "port"            { value = aws_db_instance.main.port }
output "db_name"         { value = aws_db_instance.main.db_name }
output "instance_id"     { value = aws_db_instance.main.identifier }
output "security_group_id" { value = aws_security_group.rds.id }