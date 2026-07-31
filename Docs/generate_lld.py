"""Generates Darviq_Terraform_Low_Level_Design.docx from docx_builder.
Run from inside Docs/: python generate_lld.py
"""
from docx_builder import DesignDoc

DATE = "July 31, 2026"
VERSION = "1.0"

doc = DesignDoc(
    project_name="Darviq Terraform",
    subtitle="Reusable Terraform Module Library for Core AWS Resources",
    doc_kind="Low-Level Design (LLD)",
    version=VERSION,
    date=DATE,
)
doc.add_document_control()
doc.add_toc_field()

# 1. Introduction
doc.add_heading1("1. Introduction")

doc.add_heading2("1.1 Purpose")
doc.add_paragraph(
    "This document is the low-level design companion to "
    "Darviq_Terraform_High_Level_Design.docx. Where the HLD describes module "
    "boundaries, composition order, and security intent at the level of a "
    "reader deciding whether to adopt this library, this LLD documents the "
    "literal, file-level contract of each module: every variable and output "
    "it declares, the exact resource composition inside each main.tf, the "
    "conditional (count/for_each) logic used, and the validation/lifecycle "
    "behavior actually present in the code. This is the level of detail a "
    "consumer needs to write a correct module block, and the level of detail "
    "a maintainer needs before changing a module without an unintended "
    "breaking change."
)

doc.add_heading2("1.2 Scope")
doc.add_paragraph(
    "Covers the five modules under modules/ (vpc, rds, s3-bucket, "
    "security-group, iam-role) and the three example root configurations "
    "under examples/ (rds-mysql, s3-secure, iam-irsa) exactly as they exist "
    "in the repository. Does not cover a database schema or HTTP API — this "
    "repository has neither; the closest equivalent, the module input/output "
    "variable reference, is covered in Section 3 in place of those sections."
)

doc.add_heading2("1.3 References")
doc.add_bullets([
    "Darviq_Terraform_High_Level_Design.docx (this repository's HLD, same "
    "Docs/ folder)",
    "modules/vpc/{main.tf, variables.tf, outputs.tf, versions.tf, README.md}",
    "modules/rds/{main.tf, variables.tf, outputs.tf, versions.tf, README.md}",
    "modules/s3-bucket/{main.tf, variables.tf, outputs.tf, versions.tf, README.md}",
    "modules/security-group/{main.tf, variables.tf, outputs.tf, versions.tf, README.md}",
    "modules/iam-role/{main.tf, variables.tf, outputs.tf, versions.tf, README.md}",
    "examples/rds-mysql/main.tf, examples/s3-secure/main.tf, examples/iam-irsa/main.tf",
    ".github/workflows/validate-modules.yaml",
])

# 2. Detailed module design
doc.add_heading1("2. Detailed module design")

doc.add_heading2("2.1 vpc — modules/vpc/")
doc.add_paragraph(
    "Resources created by modules/vpc/main.tf: one aws_vpc.main "
    "(enable_dns_hostnames and enable_dns_support both true); one "
    "aws_internet_gateway.main attached to it; aws_subnet.public and "
    "aws_subnet.private, each using count = length(var.public_subnet_cidrs) / "
    "length(var.private_subnet_cidrs) respectively, indexed by count.index "
    "into the corresponding CIDR and availability_zones lists; aws_eip.nat "
    "and aws_nat_gateway.main, both with count = length(var.public_subnet_cidrs) "
    "(one EIP + one NAT gateway per public subnet, each NAT gateway placed in "
    "its matching public subnet and depends_on the internet gateway "
    "explicitly); aws_route_table.public (a single shared table with a "
    "0.0.0.0/0 route to the internet gateway) and aws_route_table.private "
    "(count = length(var.private_subnet_cidrs), one table per private subnet, "
    "each routing 0.0.0.0/0 to its own indexed NAT gateway); and the "
    "corresponding aws_route_table_association resources for both public and "
    "private subnets, again count-indexed to match subnet order."
)
doc.add_paragraph(
    "Conditional/count logic: every count in this module is driven by the "
    "length of a caller-supplied list, with no default fallback — "
    "public_subnet_cidrs, private_subnet_cidrs, and availability_zones have "
    "no defaults in variables.tf (only vpc_cidr and tags do), so the module "
    "always creates as many public/private subnets as CIDRs supplied, and "
    "the three lists are implicitly expected to be the same length and "
    "index-aligned by the caller."
)

doc.add_heading2("2.2 rds — modules/rds/")
doc.add_paragraph(
    "Resources created: aws_db_subnet_group.main from var.subnet_ids; "
    "aws_security_group.rds with a single ingress rule (var.port, TCP, "
    "restricted to var.allowed_cidr_blocks) and an allow-all egress rule; "
    "aws_db_instance.main wired to that security group and subnet group, "
    "with storage_type fixed to gp3 and storage_encrypted, publicly_accessible "
    "(false), performance_insights_enabled, and monitoring_interval (60) all "
    "hardcoded rather than exposed as variables; aws_iam_role.rds_monitoring "
    "with an inline assume-role policy scoped to the monitoring.rds.amazonaws.com "
    "service principal; and aws_iam_role_policy_attachment.rds_monitoring "
    "attaching the AWS-managed AmazonRDSEnhancedMonitoringRole policy to that "
    "role, whose ARN is then passed into aws_db_instance.main.monitoring_role_arn."
)
doc.add_paragraph(
    "Conditional logic: final_snapshot_identifier uses an inline conditional "
    "expression, var.skip_final_snapshot ? null : \"${var.identifier}-final-"
    "snapshot\" — a snapshot identifier is only generated when a final "
    "snapshot will actually be taken, avoiding an unused identifier when "
    "skip_final_snapshot is true. There is no count/for_each in this module — "
    "it always creates exactly one instance, one security group, one subnet "
    "group, and one monitoring role per module call."
)

doc.add_heading2("2.3 s3-bucket — modules/s3-bucket/")
doc.add_paragraph(
    "Resources created: aws_s3_bucket.main; aws_s3_bucket_versioning.main "
    "(status driven by var.versioning_enabled ? \"Enabled\" : \"Suspended\"); "
    "aws_s3_bucket_server_side_encryption_configuration.main, whose "
    "sse_algorithm is var.kms_key_arn != null ? \"aws:kms\" : \"AES256\" and "
    "whose bucket_key_enabled mirrors that same null check; "
    "aws_s3_bucket_public_access_block.main with all four flags hardcoded "
    "true (block_public_acls, block_public_policy, ignore_public_acls, "
    "restrict_public_buckets) and no corresponding variable; "
    "aws_s3_bucket_lifecycle_configuration.main, gated by "
    "count = length(var.lifecycle_rules) > 0 ? 1 : 0 so the resource is "
    "omitted entirely when no lifecycle rules are supplied, and internally "
    "using a dynamic \"rule\" block iterating var.lifecycle_rules to emit one "
    "transition + one expiration block per rule; and "
    "aws_s3_bucket_logging.main, gated by count = var.logging_bucket != null "
    "? 1 : 0, writing access logs to var.logging_bucket under a "
    "\"${var.bucket_name}/\" prefix."
)
doc.add_paragraph(
    "Conditional logic: this module has the highest density of optional-"
    "resource patterns in the library — both the lifecycle configuration and "
    "the logging configuration use the count = <condition> ? 1 : 0 idiom to "
    "make an entire resource optional, rather than making individual "
    "arguments optional within an always-present resource."
)

doc.add_heading2("2.4 security-group — modules/security-group/")
doc.add_paragraph(
    "Resources created: aws_security_group.main (with an explicit lifecycle "
    "{ create_before_destroy = true } block); aws_security_group_rule.ingress "
    "using for_each = { for idx, rule in var.ingress_rules : idx => rule } "
    "— i.e. keyed by list index rather than by a natural key from the rule "
    "itself — reading cidr_blocks and source_sg_id via lookup(each.value, "
    "\"cidr_blocks\", null) / lookup(each.value, \"source_sg_id\", null) so "
    "either, both, or neither can be set per rule; and a single "
    "aws_security_group_rule.egress resource (not for_each — always exactly "
    "one, allow-all, all protocols, 0.0.0.0/0)."
)
doc.add_paragraph(
    "Conditional logic: because the ingress for_each is keyed by index, "
    "removing a rule from the middle of var.ingress_rules shifts the "
    "for_each keys of every following rule, which Terraform will treat as "
    "in-place resource replacement for those shifted rules rather than a "
    "single deletion — a caller changing ingress_rules should be aware the "
    "diff may be larger than the actual rule-set change if a rule is removed "
    "from anywhere but the end of the list."
)

doc.add_heading2("2.5 iam-role — modules/iam-role/")
doc.add_paragraph(
    "Resources/data sources: local.is_irsa = var.oidc_provider_arn != null "
    "&& var.service_account_name != null; "
    "data.aws_iam_policy_document.trust_ec2, gated by "
    "count = var.trusted_service != null && !local.is_irsa ? 1 : 0, building "
    "an sts:AssumeRole statement for the var.trusted_service principal; "
    "data.aws_iam_policy_document.trust_irsa, gated by "
    "count = local.is_irsa ? 1 : 0, building an "
    "sts:AssumeRoleWithWebIdentity statement for a Federated principal "
    "(var.oidc_provider_arn) with two condition blocks — a StringEquals on "
    "\"<oidc-host>:sub\" restricting to "
    "system:serviceaccount:<namespace>:<service_account_name>, and a second "
    "StringEquals on \"<oidc-host>:aud\" restricting to sts.amazonaws.com — "
    "where <oidc-host> is derived via "
    "replace(var.oidc_provider_arn, \"/^.*oidc-provider\\\\//\", \"\") to strip "
    "the ARN prefix down to the bare OIDC issuer host/path; "
    "aws_iam_role.main, whose assume_role_policy is a ternary picking "
    "trust_irsa[0].json when local.is_irsa else trust_ec2[0].json; "
    "aws_iam_role_policy_attachment.managed using "
    "for_each = toset(var.managed_policy_arns) (deduplicated via toset, so "
    "each unique ARN gets exactly one attachment regardless of list order); "
    "and aws_iam_role_policy.inline, gated by "
    "count = var.inline_policy_json != null ? 1 : 0."
)
doc.add_paragraph(
    "Conditional logic: the module relies on exactly one of the two "
    "count-gated policy documents ever being length 1 for a given call — if "
    "var.trusted_service is left null and local.is_irsa is also false (i.e. "
    "neither trust mechanism's inputs are supplied), both "
    "data.aws_iam_policy_document resources have count = 0 and the "
    "assume_role_policy ternary would reference an out-of-bounds index "
    "([0] on a zero-length resource), which fails at plan time. In practice "
    "this means var.trusted_service is a soft requirement whenever IRSA "
    "variables are not set, even though variables.tf does not mark it "
    "required at the type level (see Section 6)."
)

# 3. Module input/output variable reference
doc.add_heading1("3. Module input/output variable reference")
doc.add_paragraph(
    "This section replaces a database schema / API specification section: "
    "for a Terraform module library, the variable/output contract of each "
    "module is the literal interface a consumer codes against, transcribed "
    "directly from each module's variables.tf and outputs.tf."
)

doc.add_heading2("3.1 vpc")
doc.add_table(
    headers=["Variable", "Type", "Default", "Required", "Description"],
    rows=[
        ["project_name", "string", "n/a", "Yes", "Project name for resource naming"],
        ["cluster_name", "string", "n/a", "Yes", "EKS cluster name for subnet tags"],
        ["vpc_cidr", "string", '"10.0.0.0/16"', "No", "CIDR block for the VPC"],
        ["public_subnet_cidrs", "list(string)", "n/a", "Yes", "CIDR blocks for the public subnets, one per availability zone"],
        ["private_subnet_cidrs", "list(string)", "n/a", "Yes", "CIDR blocks for the private subnets, one per availability zone"],
        ["availability_zones", "list(string)", "n/a", "Yes", "Availability zones to spread the public/private subnets across"],
        ["tags", "map(string)", "{}", "No", "Common tags applied to all resources created by this module"],
    ],
)
doc.add_table(
    headers=["Output", "Description"],
    rows=[
        ["vpc_id", "ID of the created VPC"],
        ["public_subnet_ids", "IDs of the public subnets"],
        ["private_subnet_ids", "IDs of the private subnets"],
    ],
)

doc.add_heading2("3.2 rds")
doc.add_table(
    headers=["Variable", "Type", "Default", "Required", "Description"],
    rows=[
        ["identifier", "string", "n/a", "Yes", "Unique identifier used for the RDS instance and related resources (subnet group, security group)"],
        ["vpc_id", "string", "n/a", "Yes", "ID of the VPC where the RDS instance and its security group will be created"],
        ["subnet_ids", "list(string)", "n/a", "Yes", "Subnet IDs to place the RDS instance in (used to build the DB subnet group)"],
        ["allowed_cidr_blocks", "list(string)", "n/a", "Yes", "CIDR blocks allowed to reach the database port via the instance's security group"],
        ["engine", "string", '"mysql"', "No", "Database engine to use (e.g. mysql, postgres)"],
        ["engine_version", "string", '"8.0"', "No", "Engine version for the database instance"],
        ["instance_class", "string", '"db.t3.micro"', "No", "RDS instance class (e.g. db.t3.micro)"],
        ["allocated_storage", "number", "20", "No", "Allocated storage size in GB for the RDS instance"],
        ["database_name", "string", "n/a", "Yes", "Name of the initial database to create"],
        ["username", "string", "n/a", "Yes", "Master username for the database"],
        ["password", "string (sensitive)", "n/a", "Yes", "Master password; source from a secrets manager, not a checked-in tfvars file"],
        ["port", "number", "3306", "No", "Port the database listens on"],
        ["multi_az", "bool", "false", "No", "Whether to enable Multi-AZ deployment for high availability"],
        ["backup_retention_days", "number", "7", "No", "Number of days to retain automated backups"],
        ["deletion_protection", "bool", "true", "No", "Whether to enable deletion protection (defaults to true to prevent accidental deletion in production)"],
        ["skip_final_snapshot", "bool", "false", "No", "Whether to skip a final snapshot on destroy (defaults to false so a snapshot is taken unless explicitly opted out)"],
        ["tags", "map(string)", "{}", "No", "Common tags applied to all resources created by this module"],
    ],
)
doc.add_table(
    headers=["Output", "Description"],
    rows=[
        ["endpoint", "Connection endpoint (host:port) for the RDS instance"],
        ["port", "Port the RDS instance is listening on"],
        ["db_name", "Name of the initial database created on the instance"],
        ["instance_id", "Identifier of the RDS instance"],
        ["security_group_id", "ID of the security group attached to the RDS instance"],
    ],
)

doc.add_heading2("3.3 s3-bucket")
doc.add_table(
    headers=["Variable", "Type", "Default", "Required", "Description"],
    rows=[
        ["bucket_name", "string", "n/a", "Yes", "Name of the S3 bucket to create"],
        ["versioning_enabled", "bool", "true", "No", "Whether to enable versioning on the bucket"],
        ["kms_key_arn", "string", "null", "No", "ARN of a KMS key for SSE-KMS; falls back to AES256 (SSE-S3) when null — encryption is always enabled either way"],
        ["logging_bucket", "string", "null", "No", "Target bucket for S3 access logs; access logging disabled when null"],
        ["lifecycle_rules", "list(object({ id, enabled, transition_days, storage_class, expiration_days }))", "[]", "No", "Lifecycle transition/expiration rules to apply to bucket objects; no rules by default"],
        ["tags", "map(string)", "{}", "No", "Common tags applied to the bucket"],
    ],
)
doc.add_table(
    headers=["Output", "Description"],
    rows=[
        ["bucket_id", "ID of the created S3 bucket"],
        ["bucket_arn", "ARN of the created S3 bucket"],
        ["bucket_name", "Name of the created S3 bucket"],
    ],
)

doc.add_heading2("3.4 security-group")
doc.add_table(
    headers=["Variable", "Type", "Default", "Required", "Description"],
    rows=[
        ["name", "string", "n/a", "Yes", "Name of the security group"],
        ["description", "string", "n/a", "Yes", "Description of the security group"],
        ["vpc_id", "string", "n/a", "Yes", "ID of the VPC where the security group will be created"],
        ["ingress_rules", "list(object({ from_port, to_port, protocol, description, cidr_blocks = optional, source_sg_id = optional }))", "[]", "No", "Ingress rules to attach; empty by default so no ports are open unless explicitly requested"],
        ["tags", "map(string)", "{}", "No", "Common tags applied to the security group"],
    ],
)
doc.add_table(
    headers=["Output", "Description"],
    rows=[
        ["security_group_id", "ID of the created security group"],
        ["security_group_arn", "ARN of the created security group"],
    ],
)

doc.add_heading2("3.5 iam-role")
doc.add_table(
    headers=["Variable", "Type", "Default", "Required", "Description"],
    rows=[
        ["role_name", "string", "n/a", "Yes", "Name of the IAM role"],
        ["trusted_service", "string", "null", "No*", "AWS service principal (e.g. ec2.amazonaws.com, lambda.amazonaws.com) allowed to assume this role; ignored when IRSA variables are set. *Effectively required whenever IRSA variables are not both set — see Section 2.5/6"],
        ["oidc_provider_arn", "string", "null", "No", "ARN of the EKS OIDC provider; combined with service_account_name, switches the trust policy to IRSA"],
        ["service_account_name", "string", "null", "No", "Kubernetes service account name to federate via IRSA"],
        ["service_account_namespace", "string", '"default"', "No", "Kubernetes namespace of the service account for IRSA trust policy"],
        ["managed_policy_arns", "list(string)", "[]", "No", "Managed IAM policy ARNs to attach to the role"],
        ["inline_policy_json", "string", "null", "No", "Inline IAM policy document (JSON) to attach; no inline policy created when null"],
        ["tags", "map(string)", "{}", "No", "Common tags applied to the role"],
    ],
)
doc.add_table(
    headers=["Output", "Description"],
    rows=[
        ["role_arn", "ARN of the created IAM role"],
        ["role_name", "Name of the created IAM role"],
    ],
)

doc.add_heading2("3.6 Module usage examples")
doc.add_paragraph("From examples/rds-mysql/main.tf:")
doc.add_code_block(
    'module "mysql" {\n'
    '  source = "../../modules/rds"\n\n'
    '  identifier          = "platform-mysql-dev"\n'
    '  vpc_id              = "vpc-xxxxxxxx"\n'
    '  subnet_ids          = ["subnet-aaa", "subnet-bbb"]\n'
    '  allowed_cidr_blocks = ["10.0.0.0/16"]\n\n'
    '  database_name = "appdb"\n'
    '  username      = "admin"\n'
    '  password      = "change-me-use-secrets-manager"\n\n'
    '  instance_class        = "db.t3.micro"\n'
    '  multi_az              = false\n'
    '  backup_retention_days = 7\n'
    '  deletion_protection   = false\n'
    '  skip_final_snapshot   = true\n\n'
    '  tags = { Environment = "dev", ManagedBy = "terraform" }\n'
    "}\n\n"
    'output "mysql_endpoint" { value = module.mysql.endpoint }'
)
doc.add_paragraph("From examples/s3-secure/main.tf:")
doc.add_code_block(
    'module "app_bucket" {\n'
    '  source = "../../modules/s3-bucket"\n\n'
    '  bucket_name        = "my-app-assets-dev-123456"\n'
    '  versioning_enabled = true\n\n'
    "  lifecycle_rules = [{\n"
    '    id              = "move-to-ia"\n'
    "    enabled         = true\n"
    "    transition_days = 90\n"
    '    storage_class   = "STANDARD_IA"\n'
    "    expiration_days = 365\n"
    "  }]\n\n"
    '  tags = { Environment = "dev", ManagedBy = "terraform" }\n'
    "}\n\n"
    'output "bucket_arn" { value = module.app_bucket.bucket_arn }'
)
doc.add_paragraph("From examples/iam-irsa/main.tf:")
doc.add_code_block(
    'module "s3_reader_role" {\n'
    '  source = "../../modules/iam-role"\n\n'
    '  role_name                 = "platform-s3-reader"\n'
    '  oidc_provider_arn         = "arn:aws:iam::123456:oidc-provider/oidc.eks.ap-south-1.amazonaws.com/id/XXXXX"\n'
    '  service_account_name      = "s3-reader"\n'
    '  service_account_namespace = "apps"\n\n'
    "  inline_policy_json = jsonencode({\n"
    '    Version = "2012-10-17"\n'
    "    Statement = [{\n"
    '      Effect   = "Allow"\n'
    '      Action   = ["s3:GetObject", "s3:ListBucket"]\n'
    '      Resource = ["arn:aws:s3:::my-app-assets-dev-123456/*"]\n'
    "    }]\n"
    "  })\n\n"
    '  tags = { ManagedBy = "terraform" }\n'
    "}\n\n"
    'output "role_arn" { value = module.s3_reader_role.role_arn }'
)
doc.add_paragraph(
    "No committed example currently composes vpc with security-group/rds "
    "(Section 8 of the HLD); the composed example below is illustrative, "
    "following the same conventions as the committed examples above, and "
    "is not itself present as a file in this repository:"
)
doc.add_code_block(
    'module "vpc" {\n'
    '  source = "../../modules/vpc"\n\n'
    '  project_name         = "platform"\n'
    '  cluster_name         = "platform-eks"\n'
    '  availability_zones   = ["ap-south-1a", "ap-south-1b"]\n'
    '  public_subnet_cidrs  = ["10.0.0.0/24", "10.0.1.0/24"]\n'
    '  private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]\n'
    '  tags = { Environment = "dev" }\n'
    "}\n\n"
    'module "db_sg_source" {\n'
    '  source = "../../modules/security-group"\n\n'
    '  name        = "app-to-db"\n'
    '  description = "Application tier"\n'
    "  vpc_id      = module.vpc.vpc_id\n"
    '  tags        = { Environment = "dev" }\n'
    "}\n\n"
    'module "mysql" {\n'
    '  source = "../../modules/rds"\n\n'
    '  identifier          = "platform-mysql-dev"\n'
    "  vpc_id              = module.vpc.vpc_id\n"
    "  subnet_ids          = module.vpc.private_subnet_ids\n"
    '  allowed_cidr_blocks = ["10.0.10.0/24", "10.0.11.0/24"]\n'
    "  # ... remaining rds variables as shown above\n"
    "}"
)

# 4. Sequence flows / process flows
doc.add_heading1("4. Sequence flows / process flows")

doc.add_heading2("4.1 Provisioning a new VPC + security group + RDS instance together")
doc.add_table(
    headers=["Step", "Actor/Component", "Action"],
    rows=[
        ["1", "Consumer root module", "Declares module \"vpc\" { source = \"modules/vpc\" ... } with "
         "project_name, cluster_name, availability_zones, and the two CIDR lists"],
        ["2", "terraform apply", "Creates aws_vpc.main, aws_internet_gateway.main, subnets, NAT "
         "gateways/EIPs, and route tables/associations (Section 2.1); vpc_id and "
         "private_subnet_ids become available as module outputs"],
        ["3", "Consumer root module", "Declares module \"security-group\" or relies on rds's own "
         "internal security group, passing module.vpc.vpc_id as vpc_id"],
        ["4", "Consumer root module", "Declares module \"rds\" { source = \"modules/rds\" ... }, "
         "passing module.vpc.vpc_id and module.vpc.private_subnet_ids as vpc_id/subnet_ids, "
         "and a CIDR list (e.g. the VPC's private subnet ranges) as allowed_cidr_blocks"],
        ["5", "terraform apply", "Terraform's dependency graph (built from the output references "
         "in steps 3-4) applies vpc first, then rds's aws_db_subnet_group.main, "
         "aws_security_group.rds, aws_iam_role.rds_monitoring, and finally "
         "aws_db_instance.main"],
        ["6", "Consumer root module", "Reads module.mysql.endpoint (host:port) to configure the "
         "consuming application"],
    ],
)

doc.add_heading2("4.2 Provisioning a secure S3 bucket with lifecycle rules (examples/s3-secure)")
doc.add_table(
    headers=["Step", "Actor/Component", "Action"],
    rows=[
        ["1", "Consumer root module", "Declares module \"app_bucket\" with bucket_name, "
         "versioning_enabled = true, and one entry in lifecycle_rules"],
        ["2", "terraform apply", "Creates aws_s3_bucket.main, aws_s3_bucket_versioning.main "
         "(status = Enabled), aws_s3_bucket_server_side_encryption_configuration.main "
         "(AES256, since kms_key_arn is not set), and aws_s3_bucket_public_access_block.main"],
        ["3", "terraform apply", "Because length(var.lifecycle_rules) > 0, "
         "aws_s3_bucket_lifecycle_configuration.main[0] is also created, with a dynamic "
         "rule block emitting the move-to-ia transition (STANDARD_IA at 90 days) and "
         "expiration (365 days)"],
        ["4", "terraform apply", "aws_s3_bucket_logging.main is skipped (count = 0) because "
         "logging_bucket is not set in this example"],
        ["5", "Consumer root module", "Reads module.app_bucket.bucket_arn, e.g. to reference it "
         "from an iam-role module's inline_policy_json Resource list (Section 4.3)"],
    ],
)

doc.add_heading2("4.3 Provisioning an EKS IRSA role scoped to a specific S3 bucket (examples/iam-irsa)")
doc.add_table(
    headers=["Step", "Actor/Component", "Action"],
    rows=[
        ["1", "Consumer root module", "Declares module \"s3_reader_role\" with role_name, "
         "oidc_provider_arn (an existing EKS cluster's OIDC provider), service_account_name, "
         "and service_account_namespace"],
        ["2", "iam-role module logic", "local.is_irsa evaluates true (both oidc_provider_arn and "
         "service_account_name are set), so data.aws_iam_policy_document.trust_irsa[0] is "
         "built and data.aws_iam_policy_document.trust_ec2 has count = 0"],
        ["3", "terraform apply", "aws_iam_role.main is created with the IRSA trust policy as its "
         "assume_role_policy"],
        ["4", "terraform apply", "aws_iam_role_policy.inline[0] is created (count = 1, since "
         "inline_policy_json is set) attaching the s3:GetObject/s3:ListBucket statement "
         "scoped to a specific bucket ARN"],
        ["5", "Consumer root module", "Reads module.s3_reader_role.role_arn to annotate the "
         "Kubernetes ServiceAccount (eks.amazonaws.com/role-arn) outside this repository's "
         "scope (Kubernetes manifests are not managed by this Terraform library)"],
    ],
)

# 5. Key algorithms & business logic
doc.add_heading1("5. Key algorithms & business logic")
doc.add_heading2("5.1 Index-driven subnet/NAT fan-out (modules/vpc/main.tf)")
doc.add_paragraph(
    "Rather than a fixed number of AZs, every count in modules/vpc/main.tf "
    "(aws_subnet.public, aws_subnet.private, aws_eip.nat, aws_nat_gateway.main, "
    "aws_route_table.private, and both route-table-association resources) is "
    "driven by length(var.public_subnet_cidrs) or "
    "length(var.private_subnet_cidrs), and each resource instance reads its "
    "own CIDR/AZ/NAT-gateway/subnet via count.index into the matching list. "
    "This is the module's core 'algorithm': N public CIDRs + N private CIDRs "
    "+ N AZs deterministically produces N public subnets, N private subnets, "
    "N EIPs, N NAT gateways, N private route tables, and one shared public "
    "route table — a 1:1:1 fan-out per index rather than a fixed topology."
)
doc.add_heading2("5.2 Implicit trust-policy selection (modules/iam-role/main.tf)")
doc.add_paragraph(
    "local.is_irsa = var.oidc_provider_arn != null && var.service_account_name "
    "!= null acts as the module's only branch point, gating which of the two "
    "count-conditional data.aws_iam_policy_document resources is built, and "
    "which of the two is referenced by the assume_role_policy ternary on "
    "aws_iam_role.main. The OIDC host used inside the IRSA trust condition's "
    "variable keys (\"<host>:sub\", \"<host>:aud\") is derived at plan time via "
    "a regex-based replace() that strips everything up to and including "
    "oidc-provider/ from var.oidc_provider_arn, rather than requiring the "
    "caller to pass the bare issuer host separately."
)
doc.add_heading2("5.3 Optional-resource-via-count idiom (modules/s3-bucket, modules/iam-role)")
doc.add_paragraph(
    "Both aws_s3_bucket_lifecycle_configuration.main and "
    "aws_s3_bucket_logging.main in modules/s3-bucket/main.tf, and "
    "aws_iam_role_policy.inline in modules/iam-role/main.tf, use the same "
    "count = <condition> ? 1 : 0 idiom to make an entire resource "
    "conditionally exist based on whether an optional variable "
    "(lifecycle_rules, logging_bucket, inline_policy_json) was populated. "
    "This is the library's consistent pattern for 'this resource is optional' "
    "as opposed to for_each, which the library reserves for '0-to-many "
    "repeated resources of the same kind' (aws_security_group_rule.ingress, "
    "aws_iam_role_policy_attachment.managed)."
)
doc.add_heading2("5.4 Conditional encryption algorithm selection (modules/s3-bucket/main.tf)")
doc.add_paragraph(
    "sse_algorithm = var.kms_key_arn != null ? \"aws:kms\" : \"AES256\" paired "
    "with bucket_key_enabled = var.kms_key_arn != null means the presence of "
    "a KMS key ARN is the sole signal switching the bucket from SSE-S3 to "
    "SSE-KMS (and simultaneously enabling the S3 Bucket Key optimization that "
    "only makes sense under SSE-KMS) — there is no separate boolean toggling "
    "encryption on/off, consistent with the module's 'always encrypted' design "
    "intent from the HLD."
)

# 6. Validation & error handling
doc.add_heading1("6. Validation & error handling")
doc.add_paragraph(
    "None of the five modules currently declare a variable { validation { ... "
    "} } block, and none use a precondition/postcondition lifecycle rule. "
    "The only lifecycle customization present anywhere in the library is "
    "modules/security-group/main.tf's aws_security_group.main resource, which "
    "sets lifecycle { create_before_destroy = true } so a security group "
    "replacement provisions the new group before destroying the old one, "
    "avoiding a brief window where dependents reference a deleted group."
)
doc.add_paragraph("Known gaps in validation/error handling, observed directly in the code:")
doc.add_bullets([
    "modules/vpc: no validation that public_subnet_cidrs, private_subnet_cidrs, "
    "and availability_zones are the same length — a mismatch surfaces as a "
    "Terraform index-out-of-range error at plan/apply time rather than a "
    "named validation message (Section 2.1).",
    "modules/iam-role: no validation that at least one of trusted_service or "
    "(oidc_provider_arn + service_account_name) is supplied — omitting both "
    "produces a [0] index error on an empty data source list rather than a "
    "clear message (Section 2.5).",
    "modules/rds: password is marked sensitive = true (so its value is "
    "redacted from plan/apply console output and state diffs shown in the "
    "CLI) but has no length/complexity validation block — an invalid value "
    "would only be caught by the AWS API at apply time.",
    "modules/s3-bucket: lifecycle_rules is a list(object({...})) with all "
    "fields required inside the object type; a caller omitting a field (e.g. "
    "expiration_days) gets a Terraform type-constraint error at plan time, "
    "which is Terraform's own type-checking rather than a module-authored "
    "validation message.",
])
doc.add_paragraph(
    "Error handling for AWS-side failures (e.g. an invalid CIDR overlapping "
    "an existing VPC, an RDS instance class unavailable in the target region) "
    "is entirely delegated to the AWS provider/API and surfaces as a "
    "standard Terraform apply-time error; no module wraps or retries these."
)

# 7. Non-functional implementation details
doc.add_heading1("7. Non-functional implementation details")
doc.add_heading2("7.1 Versioning and provider constraints")
doc.add_paragraph(
    "Every module and example declares an identical terraform { "
    "required_version = \">= 1.7.0\" required_providers { aws = { source = "
    "\"hashicorp/aws\" version = \"~> 6.0\" } } } block in its own versions.tf "
    "— there is no shared/centralized version file, so each module's "
    "constraint could in principle drift independently, though today all six "
    "versions.tf files (5 modules + one per example) are identical. Each "
    "module and example also has its own .terraform.lock.hcl recording the "
    "exact resolved AWS provider build (6.50.0 at the time of writing)."
)
doc.add_heading2("7.2 Tagging convention")
doc.add_paragraph(
    "Every module accepts a tags variable (type map(string), default {}) and "
    "applies it via merge(var.tags, { Name = \"...\" }) on its primary "
    "resource(s) — vpc merges a computed Name per resource (e.g. "
    "\"${var.project_name}-vpc\", \"${var.project_name}-public-1\"), rds and "
    "security-group merge a Name from their identifier/name variable, and "
    "iam-role/s3-bucket apply var.tags directly without an additional "
    "computed Name (their primary resource's own name argument already "
    "serves that purpose)."
)
doc.add_heading2("7.3 CI as the only automated non-functional gate")
doc.add_paragraph(
    ".github/workflows/validate-modules.yaml runs a 5-way matrix (one job per "
    "module: vpc, rds, s3-bucket, security-group, iam-role), each performing "
    "terraform fmt -check -recursive against that module's directory, "
    "terraform init -backend=false, terraform validate, and tflint --init && "
    "tflint. This is a syntax/style/static-analysis gate only — it does not "
    "run terraform plan against real AWS credentials, so it cannot catch "
    "issues that only manifest against live AWS state (e.g. a CIDR overlap, "
    "an IAM policy that AWS itself rejects)."
)

# 8. Appendix
doc.add_heading1("8. Appendix")

doc.add_heading2("8.1 Repo module/file map")
doc.add_code_block(
    "Darviq-Terraform/\n"
    "  README.md\n"
    "  .github/\n"
    "    workflows/\n"
    "      validate-modules.yaml\n"
    "  modules/\n"
    "    vpc/\n"
    "      main.tf          # aws_vpc, igw, subnets, NAT/EIP, route tables\n"
    "      variables.tf     # project_name, cluster_name, vpc_cidr, subnet CIDRs, AZs, tags\n"
    "      outputs.tf       # vpc_id, public_subnet_ids, private_subnet_ids\n"
    "      versions.tf      # terraform >= 1.7.0, aws ~> 6.0\n"
    "      README.md\n"
    "    rds/\n"
    "      main.tf          # aws_db_instance, dedicated SG, subnet group, monitoring role\n"
    "      variables.tf     # identifier, vpc_id, subnet_ids, allowed_cidr_blocks, engine, ...\n"
    "      outputs.tf       # endpoint, port, db_name, instance_id, security_group_id\n"
    "      versions.tf\n"
    "      README.md\n"
    "    s3-bucket/\n"
    "      main.tf          # aws_s3_bucket + versioning/encryption/PAB/lifecycle/logging\n"
    "      variables.tf     # bucket_name, versioning_enabled, kms_key_arn, lifecycle_rules, ...\n"
    "      outputs.tf       # bucket_id, bucket_arn, bucket_name\n"
    "      versions.tf\n"
    "      README.md\n"
    "    security-group/\n"
    "      main.tf          # aws_security_group + ingress (for_each) + egress (allow-all)\n"
    "      variables.tf     # name, description, vpc_id, ingress_rules, tags\n"
    "      outputs.tf       # security_group_id, security_group_arn\n"
    "      versions.tf\n"
    "      README.md\n"
    "    iam-role/\n"
    "      main.tf          # trust-policy selection, role, managed/inline policy attach\n"
    "      variables.tf     # role_name, trusted_service, oidc_provider_arn, ...\n"
    "      outputs.tf       # role_arn, role_name\n"
    "      versions.tf\n"
    "      README.md\n"
    "  examples/\n"
    "    rds-mysql/main.tf      # calls modules/rds\n"
    "    s3-secure/main.tf      # calls modules/s3-bucket with lifecycle_rules\n"
    "    iam-irsa/main.tf       # calls modules/iam-role for an EKS IRSA role\n"
    "  Docs/\n"
    "    Darviq_Terraform_High_Level_Design.docx\n"
    "    Darviq_Terraform_Low_Level_Design.docx\n"
    "    docx_builder.py        # shared doc-generation helper (kept for regeneration)\n"
    "    generate_hld.py        # regenerates the HLD\n"
    "    generate_lld.py        # regenerates this LLD"
)

doc.add_heading2("8.2 Consolidated module/source path table")
doc.add_table(
    headers=["Module", "Source path", "Primary resource(s)"],
    rows=[
        ["vpc", "modules/vpc", "aws_vpc, aws_internet_gateway, aws_subnet (x2), aws_nat_gateway, aws_route_table (x2)"],
        ["rds", "modules/rds", "aws_db_instance, aws_security_group, aws_db_subnet_group, aws_iam_role (monitoring)"],
        ["s3-bucket", "modules/s3-bucket", "aws_s3_bucket + versioning/encryption/public-access-block/lifecycle/logging sub-resources"],
        ["security-group", "modules/security-group", "aws_security_group, aws_security_group_rule (ingress for_each, egress single)"],
        ["iam-role", "modules/iam-role", "aws_iam_role, aws_iam_policy_document (ec2/irsa), aws_iam_role_policy_attachment, aws_iam_role_policy"],
    ],
)

doc.add_heading2("8.3 Change history")
doc.add_table(
    headers=["Version", "Date", "Description"],
    rows=[[VERSION, DATE, "Initial low-level design document"]],
)

doc.save("Darviq_Terraform_Low_Level_Design.docx")
print("LLD saved.")
