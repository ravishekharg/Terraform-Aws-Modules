variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket to create"
}

variable "versioning_enabled" {
  type        = bool
  default     = true
  description = "Whether to enable versioning on the bucket. Defaults to true"
}

variable "kms_key_arn" {
  type        = string
  default     = null
  description = "ARN of a KMS key used for server-side encryption. When null, the bucket falls back to AES256 (SSE-S3); encryption is always enabled either way"
}

variable "logging_bucket" {
  type        = string
  default     = null
  description = "Name of the target bucket to send S3 access logs to. When null, access logging is disabled"
}

variable "lifecycle_rules" {
  type = list(object({
    id              = string
    enabled         = bool
    transition_days = number
    storage_class   = string
    expiration_days = number
  }))
  default     = []
  description = "List of lifecycle rules (transition and expiration) to apply to bucket objects. Empty by default (no lifecycle rules)"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags applied to the bucket"
}
