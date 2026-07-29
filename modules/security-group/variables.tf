variable "name" {
  type        = string
  description = "Name of the security group"
}

variable "description" {
  type        = string
  description = "Description of the security group"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where the security group will be created"
}

variable "ingress_rules" {
  type = list(object({
    from_port    = number
    to_port      = number
    protocol     = string
    description  = string
    cidr_blocks  = optional(list(string))
    source_sg_id = optional(string)
  }))
  default     = []
  description = "List of ingress rules to attach to the security group. Empty by default; callers must explicitly define any rule, including its cidr_blocks or source_sg_id, so no ingress is open unless requested"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags applied to the security group"
}
