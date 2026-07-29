# s3-bucket

Provisions an S3 bucket with versioning, server-side encryption, public
access blocking, and optional lifecycle rules / access logging.

Security defaults baked into this module (not configurable, by design):
- `aws_s3_bucket_public_access_block` always blocks public ACLs, public
  policies, and restricts public bucket access — there is no "public" mode
- Server-side encryption is always applied: `aws:kms` when `kms_key_arn` is
  set, otherwise `AES256` (SSE-S3) — the bucket is never left unencrypted

## Requirements

| Name | Version |
|------|---------|
| Terraform | >= 1.7.0 |
| AWS Provider | ~> 6.0 |

## Usage

See [examples/s3-secure](../../examples/s3-secure/) for a complete, runnable
example with lifecycle rules.

```hcl
module "app_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name        = "my-app-assets-dev-123456"
  versioning_enabled = true

  tags = { Environment = "dev" }
}
```

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bucket_name` | `string` | n/a | Name of the S3 bucket to create |
| `versioning_enabled` | `bool` | `true` | Whether to enable versioning on the bucket |
| `kms_key_arn` | `string` | `null` | KMS key ARN for SSE-KMS; falls back to AES256 (SSE-S3) when null |
| `logging_bucket` | `string` | `null` | Target bucket for S3 access logs; logging disabled when null |
| `lifecycle_rules` | `list(object({...}))` | `[]` | Lifecycle transition/expiration rules to apply to bucket objects |
| `tags` | `map(string)` | `{}` | Common tags applied to the bucket |

## Outputs

| Name | Description |
|------|-------------|
| `bucket_id` | ID of the created S3 bucket |
| `bucket_arn` | ARN of the created S3 bucket |
| `bucket_name` | Name of the created S3 bucket |
