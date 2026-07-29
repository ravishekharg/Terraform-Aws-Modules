# vpc

Provisions a multi-AZ VPC: the VPC itself, an internet gateway, one public
and one private subnet per availability zone supplied, one NAT gateway per
public subnet (with its own Elastic IP), and the associated route tables.

Public subnets are tagged `kubernetes.io/role/elb = 1` and private subnets
`kubernetes.io/role/internal-elb = 1` / `karpenter.sh/discovery = <cluster_name>`
for use with EKS load balancers and Karpenter node discovery.

## Requirements

| Name | Version |
|------|---------|
| Terraform | >= 1.7.0 |
| AWS Provider | ~> 6.0 |

## Usage

See [examples/rds-mysql](../../examples/rds-mysql/) for a module wired to
a VPC's subnet outputs (adapt the `vpc` module call shown below):

```hcl
module "vpc" {
  source = "../../modules/vpc"

  project_name          = "platform"
  cluster_name          = "platform-eks"
  vpc_cidr              = "10.0.0.0/16"
  availability_zones    = ["ap-south-1a", "ap-south-1b"]
  public_subnet_cidrs   = ["10.0.0.0/24", "10.0.1.0/24"]
  private_subnet_cidrs  = ["10.0.10.0/24", "10.0.11.0/24"]

  tags = { Environment = "dev" }
}
```

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_name` | `string` | n/a | Project name for resource naming |
| `cluster_name` | `string` | n/a | EKS cluster name for subnet tags |
| `vpc_cidr` | `string` | `"10.0.0.0/16"` | CIDR block for the VPC |
| `public_subnet_cidrs` | `list(string)` | n/a | CIDR blocks for the public subnets, one per availability zone |
| `private_subnet_cidrs` | `list(string)` | n/a | CIDR blocks for the private subnets, one per availability zone |
| `availability_zones` | `list(string)` | n/a | Availability zones to spread the public/private subnets across |
| `tags` | `map(string)` | `{}` | Common tags applied to all resources created by this module |

## Outputs

| Name | Description |
|------|-------------|
| `vpc_id` | ID of the created VPC |
| `public_subnet_ids` | IDs of the public subnets |
| `private_subnet_ids` | IDs of the private subnets |
