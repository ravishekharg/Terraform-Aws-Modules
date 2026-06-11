module "app_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name        = "my-app-assets-dev-123456"
  versioning_enabled = true

  lifecycle_rules = [{
    id              = "move-to-ia"
    enabled         = true
    transition_days = 90
    storage_class   = "STANDARD_IA"
    expiration_days = 365
  }]

  tags = { Environment = "dev", ManagedBy = "terraform" }
}

output "bucket_arn" { value = module.app_bucket.bucket_arn }