variable "role_name"             { type = string }
variable "trusted_service"       { 
    type = string
     default = null 
}
variable "oidc_provider_arn"     { 
    type = string
    default = null 
}
variable "service_account_name"  { 
    type = string
    default = null 
}
variable "service_account_namespace" { 
    type = string
    default = "default" 
}
variable "managed_policy_arns"   { 
    type = list(string) 
    default = [] 
}
variable "inline_policy_json"    { 
    type = string
    default = null 
}
variable "tags"                  { 
    type = map(string)
    default = {} 
}