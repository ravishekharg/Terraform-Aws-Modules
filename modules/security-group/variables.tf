variable "name"        { type = string }
variable "description" { type = string }
variable "vpc_id"      { type = string }

variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    description = string
    cidr_blocks = optional(list(string))
    source_sg_id = optional(string)
  }))
  default = []
}

variable "tags" { 
  type = map(string) 
  default = {} 
}