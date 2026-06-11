# Example: IRSA role for a Kubernetes service account

module "s3_reader_role" {
  source = "../../modules/iam-role"

  role_name                 = "platform-s3-reader"
  oidc_provider_arn         = "arn:aws:iam::123456:oidc-provider/oidc.eks.ap-south-1.amazonaws.com/id/XXXXX"
  service_account_name      = "s3-reader"
  service_account_namespace = "apps"

  inline_policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:ListBucket"]
      Resource = ["arn:aws:s3:::my-app-assets-dev-123456/*"]
    }]
  })

  tags = { ManagedBy = "terraform" }
}

output "role_arn" { value = module.s3_reader_role.role_arn }