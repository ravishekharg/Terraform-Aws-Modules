# security-group

Provisions a security group with a caller-defined, opt-in list of ingress
rules and a single allow-all egress rule.

Note on defaults: `ingress_rules` defaults to an empty list — no ports are
open unless a consumer explicitly adds a rule. Egress is allow-all
(`0.0.0.0/0`, all protocols/ports), which mirrors the default AWS security
group behavior; tighten it in your own configuration if your workload
requires egress filtering.

## Requirements

| Name | Version |
|------|---------|
| Terraform | >= 1.7.0 |
| AWS Provider | ~> 6.0 |

## Usage

```hcl
module "web_sg" {
  source = "../../modules/security-group"

  name        = "web-sg"
  description = "Allow HTTPS from the internet"
  vpc_id      = "vpc-xxxxxxxx"

  ingress_rules = [{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    description = "HTTPS"
    cidr_blocks = ["0.0.0.0/0"]
  }]

  tags = { Environment = "dev" }
}
```

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `string` | n/a | Name of the security group |
| `description` | `string` | n/a | Description of the security group |
| `vpc_id` | `string` | n/a | ID of the VPC where the security group will be created |
| `ingress_rules` | `list(object({...}))` | `[]` | Ingress rules to attach; empty by default, no open ports unless specified |
| `tags` | `map(string)` | `{}` | Common tags applied to the security group |

## Outputs

| Name | Description |
|------|-------------|
| `security_group_id` | ID of the created security group |
| `security_group_arn` | ARN of the created security group |
