```markdown
# Terraform AWS Modules

![Validate](https://github.com/ravishekharg/terraform-aws-modules/actions/workflows/validate-modules.yaml/badge.svg)
![Terraform](https://img.shields.io/badge/Terraform-1.7-purple?logo=terraform)

Reusable, production-grade Terraform modules for AWS infrastructure.
Each module is independently validated, formatted, and linted via CI.

## Available Modules

| Module | Description |
|--------|-------------|
| [vpc](modules/vpc/) | Multi-AZ VPC with public/private subnets, NAT gateways |
| [eks](modules/eks/) | EKS cluster with managed node groups and OIDC |
| [rds](modules/rds/) | RDS MySQL/PostgreSQL with encryption, monitoring |
| [s3-bucket](modules/s3-bucket/) | Secure S3 with versioning, encryption, lifecycle |
| [security-group](modules/security-group/) | Flexible SG with dynamic ingress rules |
| [iam-role](modules/iam-role/) | IAM roles for EC2, Lambda, and EKS IRSA |

## Usage

Each module has a working example under `examples/`. Run any example with:

```bash
cd examples/rds-mysql
terraform init && terraform plan
```

## Design Principles
- All storage encrypted by default
- Public access blocked on S3 by default
- Least-privilege IAM patterns
- Consistent tagging via `tags` variable
- CI validates every module on every PR
```