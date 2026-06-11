# Flexible IAM role — supports EC2, Lambda, EKS IRSA, or custom trust policies

locals {
  is_irsa = var.oidc_provider_arn != null && var.service_account_name != null
}

data "aws_iam_policy_document" "trust_ec2" {
  count = var.trusted_service != null && !local.is_irsa ? 1 : 0
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = [var.trusted_service]
    }
  }
}

data "aws_iam_policy_document" "trust_irsa" {
  count = local.is_irsa ? 1 : 0
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(var.oidc_provider_arn, "/^.*oidc-provider\\//", "")}:sub"
      values   = ["system:serviceaccount:${var.service_account_namespace}:${var.service_account_name}"]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(var.oidc_provider_arn, "/^.*oidc-provider\\//", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "main" {
  name = var.role_name
  assume_role_policy = local.is_irsa ? (
    data.aws_iam_policy_document.trust_irsa[0].json
  ) : (
    data.aws_iam_policy_document.trust_ec2[0].json
  )
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "managed" {
  for_each   = toset(var.managed_policy_arns)
  role       = aws_iam_role.main.name
  policy_arn = each.value
}

resource "aws_iam_role_policy" "inline" {
  count  = var.inline_policy_json != null ? 1 : 0
  name   = "${var.role_name}-inline"
  role   = aws_iam_role.main.id
  policy = var.inline_policy_json
}