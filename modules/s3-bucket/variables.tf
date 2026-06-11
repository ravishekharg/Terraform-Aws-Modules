variable "bucket_name"         { type = string }
variable "versioning_enabled"  { 
  type = bool  
  default = true 
}
variable "kms_key_arn"         { 
  type = string 
  default = null 
}
variable "logging_bucket"      { 
  type = string 
  default = null 
}
variable "lifecycle_rules" {
  type = list(object({
    id              = string
    enabled         = bool
    transition_days = number
    storage_class   = string
    expiration_days = number
  }))
  default = []
}
variable "tags" { 
  type = map(string) 
  default = {} 
}