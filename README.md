# Terraform AWS Modules

Reusable, production-grade Terraform modules for AWS infrastructure.
Each module is independently validated, formatted, and linted via CI
(see `.github/workflows/validate-modules.yaml`).

## Requirements

| Name | Version |
|------|---------|
| Terraform | >= 1.7.0 |
| AWS Provider | ~> 6.0 |

Each module and example declares these constraints in its own `versions.tf`.
Provider credentials are supplied by the caller (e.g. via environment
variables, an AWS profile, or an assumed role) — no module hardcodes
credentials or a specific `provider "aws"` block, so consumers stay in
control of authentication and region configuration.

## Available Modules

| Module | Description |
|--------|-------------|
| [vpc](modules/vpc/) | Multi-AZ VPC with public/private subnets, an internet gateway, and one NAT gateway per public subnet |
| [rds](modules/rds/) | RDS instance (MySQL by default) with encryption at rest, a dedicated security group, enhanced monitoring, and Performance Insights |
| [s3-bucket](modules/s3-bucket/) | S3 bucket with versioning, encryption, public access always blocked, and optional lifecycle/logging |
| [security-group](modules/security-group/) | Security group with explicit, opt-in ingress rules and an allow-all egress rule |
| [iam-role](modules/iam-role/) | IAM role for EC2/Lambda-style service trust or EKS IRSA (OIDC) trust, with managed and inline policy support |

Each module has its own README under `modules/<name>/README.md` with a full
list of inputs and outputs.

## Usage

Each module has a working example under `examples/`. Run any example with:

```bash
cd examples/rds-mysql
terraform init
terraform plan
```

| Example | Demonstrates |
|---------|--------------|
| [examples/rds-mysql](examples/rds-mysql/) | Provisioning the `rds` module |
| [examples/s3-secure](examples/s3-secure/) | Provisioning the `s3-bucket` module with lifecycle rules |
| [examples/iam-irsa](examples/iam-irsa/) | Provisioning the `iam-role` module for an EKS IRSA service account |

Reference a module directly from the Terraform registry-style local path, e.g.:

```hcl
module "app_bucket" {
  source = "github.com/ravishekharg/Terraform-Aws-Modules//modules/s3-bucket"

  bucket_name = "my-app-assets"
  tags        = { Environment = "dev" }
}
```

## Design Principles
- All storage encrypted at rest by default (S3 SSE, RDS `storage_encrypted`)
- Public access blocked on S3 by default (`aws_s3_bucket_public_access_block` is unconditional, not optional)
- Security groups ship with no ingress rules by default — callers must opt in explicitly
- Least-privilege IAM patterns (scoped trust policies for IRSA, no wildcard defaults)
- Consistent tagging via a `tags` variable on every module
- CI validates formatting (`terraform fmt -check`), `terraform validate`, and `tflint` on every module, every PR

## Security Notes
- Never commit `*.tfvars` files with real credentials or `*.tfstate` files — both are excluded via `.gitignore`.
- The `rds` module's `password` variable is marked `sensitive` but still expects a real value at plan/apply time; source it from a secrets manager (e.g. AWS Secrets Manager, SSM Parameter Store) rather than a checked-in `.tfvars` file.
- The `security-group` module's `egress` rule is allow-all (`0.0.0.0/0`) by default, matching common AWS defaults; restrict it via additional rules if your workload requires egress filtering.
