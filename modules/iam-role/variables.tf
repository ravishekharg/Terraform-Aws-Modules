variable "role_name" {
  type        = string
  description = "Name of the IAM role"
}

variable "trusted_service" {
  type        = string
  default     = null
  description = "AWS service principal (e.g. ec2.amazonaws.com, lambda.amazonaws.com) allowed to assume this role. Ignored when IRSA variables are set"
}

variable "oidc_provider_arn" {
  type        = string
  default     = null
  description = "ARN of the EKS OIDC provider. When set together with service_account_name, the role trust policy is configured for IRSA instead of a service principal"
}

variable "service_account_name" {
  type        = string
  default     = null
  description = "Kubernetes service account name to federate with this role via IRSA"
}

variable "service_account_namespace" {
  type        = string
  default     = "default"
  description = "Kubernetes namespace of the service account used for IRSA trust policy"
}

variable "managed_policy_arns" {
  type        = list(string)
  default     = []
  description = "List of managed IAM policy ARNs to attach to the role"
}

variable "inline_policy_json" {
  type        = string
  default     = null
  description = "Inline IAM policy document (JSON) to attach to the role. When null, no inline policy is created"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags applied to the role"
}
