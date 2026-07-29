# iam-role

Provisions a single IAM role that supports either a standard AWS service
trust policy (EC2, Lambda, etc.) or an EKS IRSA (OIDC federated) trust
policy, plus optional managed and inline policy attachments.

The module picks the trust policy automatically: if both `oidc_provider_arn`
and `service_account_name` are set, it builds an IRSA trust policy scoped to
that OIDC provider and Kubernetes service account/namespace (with the
standard `sts.amazonaws.com` audience condition); otherwise it builds a
service-principal trust policy from `trusted_service`.

## Requirements

| Name | Version |
|------|---------|
| Terraform | >= 1.7.0 |
| AWS Provider | ~> 6.0 |

## Usage

See [examples/iam-irsa](../../examples/iam-irsa/) for a complete, runnable
IRSA example.

```hcl
module "ec2_role" {
  source = "../../modules/iam-role"

  role_name        = "app-ec2-role"
  trusted_service  = "ec2.amazonaws.com"

  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]

  tags = { Environment = "dev" }
}
```

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `role_name` | `string` | n/a | Name of the IAM role |
| `trusted_service` | `string` | `null` | AWS service principal allowed to assume this role (ignored when IRSA variables are set) |
| `oidc_provider_arn` | `string` | `null` | ARN of the EKS OIDC provider; enables IRSA trust policy when set with `service_account_name` |
| `service_account_name` | `string` | `null` | Kubernetes service account name to federate via IRSA |
| `service_account_namespace` | `string` | `"default"` | Kubernetes namespace of the service account for IRSA |
| `managed_policy_arns` | `list(string)` | `[]` | Managed IAM policy ARNs to attach to the role |
| `inline_policy_json` | `string` | `null` | Inline IAM policy document (JSON) to attach; no inline policy created when null |
| `tags` | `map(string)` | `{}` | Common tags applied to the role |

## Outputs

| Name | Description |
|------|-------------|
| `role_arn` | ARN of the created IAM role |
| `role_name` | Name of the created IAM role |
