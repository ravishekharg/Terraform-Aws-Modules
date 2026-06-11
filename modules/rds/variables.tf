variable "identifier"           { type = string }
variable "vpc_id"               { type = string }
variable "subnet_ids"           { type = list(string) }
variable "allowed_cidr_blocks"  { type = list(string) }
variable "engine"               { 
    type = string
    default = "mysql" 
}
variable "engine_version"       { 
    type = string
    default = "8.0" 
}
variable "instance_class"       { 
    type = string
    default = "db.t3.micro" 
}
variable "allocated_storage"    { 
    type = number
    default = 20 
}
variable "database_name"        { type = string }
variable "username"             { type = string }
variable "password"             { 
    type = string
    sensitive = true 
}
variable "port"                 { 
    type = number
    default = 3306 
}
variable "multi_az"             { 
    type = bool
    default = false 
}
variable "backup_retention_days"{ 
    type = number
    default = 7 
}
variable "deletion_protection"  { 
    type = bool   
    default = true 
}
variable "skip_final_snapshot"  { 
    type = bool
    default = false 
}
variable "tags"                 { 
    type = map(string) 
    default = {} 
}