"""Generates Darviq_Terraform_High_Level_Design.docx from docx_builder.
Run from inside Docs/: python generate_hld.py
"""
from docx_builder import DesignDoc

DATE = "July 31, 2026"
VERSION = "1.0"

doc = DesignDoc(
    project_name="Darviq Terraform",
    subtitle="Reusable Terraform Module Library for Core AWS Resources",
    doc_kind="High-Level Design (HLD)",
    version=VERSION,
    date=DATE,
)
doc.add_document_control()
doc.add_toc_field()

# 1. Introduction
doc.add_heading1("1. Introduction")

doc.add_heading2("1.1 Purpose")
doc.add_paragraph(
    "This document describes the high-level design of Darviq Terraform, a small, "
    "reusable Terraform module library that provisions core AWS infrastructure "
    "primitives: a multi-AZ VPC, an RDS database instance, an S3 bucket, a "
    "security group, and an IAM role. Unlike an application-level HLD, this "
    "document describes a library: its module boundaries, the contracts "
    "(inputs/outputs) each module exposes, how modules compose together, and the "
    "security defaults baked into each one. It is intended to let a reader "
    "understand the library's shape and design intent without reading every "
    ".tf file first."
)

doc.add_heading2("1.2 Scope")
doc.add_paragraph("In scope for this document:")
doc.add_bullets([
    "The five Terraform modules that ship in this repository: vpc, rds, s3-bucket, "
    "security-group, and iam-role.",
    "How a consumer composes these modules into a working deployment (module "
    "dependency order, wiring of outputs to inputs).",
    "The security-relevant defaults each module hardcodes versus what it exposes "
    "as a configurable variable.",
    "The CI validation approach (format check, terraform validate, tflint) that "
    "guards every module.",
    "The three runnable examples under examples/ that demonstrate real usage.",
])
doc.add_paragraph("Out of scope for this document:")
doc.add_bullets([
    "Any specific consuming application or environment's actual infrastructure "
    "(this is a library, not a deployed system — there is no live environment "
    "to diagram).",
    "A standalone compute (EC2 instance/Auto Scaling/EKS cluster) module. The "
    "repository's own README describes its module set as vpc, rds, s3-bucket, "
    "security-group, and iam-role only; EC2-style compute is referenced "
    "indirectly (the iam-role module can build an EC2 service-trust policy, and "
    "the vpc module tags subnets for EKS/Karpenter use), but there is no "
    "modules/ec2 directory in this repository at the time of writing. This "
    "document describes the repository as it actually exists, not as its "
    "one-line marketing description might imply.",
    "State backend provisioning (e.g. an S3 backend + DynamoDB lock table "
    "module) — the repository does not ship one; see Section 6.",
    "Terraform Cloud/Enterprise workspace configuration.",
])

doc.add_heading2("1.3 Intended audience")
doc.add_bullets([
    "Platform/DevOps engineers who want to consume these modules in their own "
    "Terraform root configurations.",
    "Reviewers evaluating the library's design and security posture before "
    "adopting it.",
    "The repository's own maintainer(s), as a reference for design decisions "
    "when extending the module set.",
])

doc.add_heading2("1.4 Definitions & abbreviations")
doc.add_table(
    headers=["Term", "Definition"],
    rows=[
        ["HCL", "HashiCorp Configuration Language, the syntax Terraform files (.tf) are written in"],
        ["Module", "A self-contained, reusable Terraform configuration unit with its own variables.tf, main.tf, and outputs.tf"],
        ["Root module / consumer", "The Terraform configuration that calls one or more of this repository's modules via a module block"],
        ["VPC", "Virtual Private Cloud — an isolated network within AWS"],
        ["NAT Gateway", "Network Address Translation gateway allowing private-subnet resources outbound internet access"],
        ["RDS", "AWS Relational Database Service"],
        ["IRSA", "IAM Roles for Service Accounts — the mechanism by which an EKS pod assumes an IAM role via OIDC federation"],
        ["OIDC", "OpenID Connect, the federation protocol IRSA trust policies rely on"],
        ["SSE", "Server-Side Encryption (S3), either SSE-S3 (AES256) or SSE-KMS"],
        ["tflint", "A Terraform-specific linter used in this repository's CI"],
        ["CIDR", "Classless Inter-Domain Routing — the notation used for subnet/VPC IP ranges"],
    ],
)

# 2. System overview
doc.add_heading1("2. System overview")

doc.add_heading2("2.1 Problem statement")
doc.add_paragraph(
    "Every AWS-based project re-solves the same handful of low-level "
    "infrastructure problems: how to lay out a VPC with public/private subnets "
    "and NAT egress, how to stand up an encrypted database with a locked-down "
    "security group, how to create an S3 bucket that isn't accidentally public, "
    "how to write a security group without leaving stray open ports, and how to "
    "write an IAM trust policy without over-granting access. Doing this "
    "correctly by hand in every new repository is repetitive and error-prone — "
    "the failure mode is usually a security default someone forgot (a public S3 "
    "bucket, an unencrypted RDS instance, an ingress rule left too broad), not a "
    "novel infrastructure requirement."
)
doc.add_paragraph(
    "Darviq Terraform exists to remove that repetition: it packages secure-by-"
    "default versions of these five building blocks once, validates them in CI "
    "on every change, and lets consumers reference them by module path instead "
    "of re-deriving the same resource blocks per project."
)

doc.add_heading2("2.2 Proposed solution summary")
doc.add_paragraph(
    "The repository is organized as a flat set of independent, single-purpose "
    "modules under modules/, each with its own variables.tf, main.tf, "
    "outputs.tf, versions.tf, and README.md. Modules do not call each other "
    "internally — composition happens in the consumer's own root configuration "
    "by wiring one module's outputs (e.g. vpc's vpc_id and subnet IDs) into "
    "another module's inputs (e.g. rds's vpc_id and subnet_ids variables). This "
    "keeps each module small, independently testable, and independently "
    "versionable, while leaving topology decisions (which modules to use "
    "together, in what order) to the consumer rather than baking them into a "
    "single monolithic module."
)
doc.add_paragraph(
    "Three runnable examples under examples/ (rds-mysql, s3-secure, iam-irsa) "
    "demonstrate this composition pattern for the rds, s3-bucket, and iam-role "
    "modules respectively."
)

# 3. Architecture overview
doc.add_heading1("3. Architecture overview")
doc.add_table(
    headers=["Component", "Responsibility", "Technology"],
    rows=[
        ["modules/vpc", "Multi-AZ network foundation: VPC, internet gateway, public/private "
         "subnets, one NAT gateway per public subnet, route tables and associations",
         "Terraform + AWS provider (aws_vpc, aws_subnet, aws_nat_gateway, aws_route_table)"],
        ["modules/rds", "Managed relational database: DB instance, dedicated security group, "
         "DB subnet group, and an IAM role for enhanced monitoring",
         "Terraform + AWS provider (aws_db_instance, aws_db_subnet_group, aws_security_group)"],
        ["modules/s3-bucket", "Object storage with encryption, versioning, public-access blocking, "
         "and optional lifecycle rules / access logging",
         "Terraform + AWS provider (aws_s3_bucket and related sub-resources)"],
        ["modules/security-group", "Standalone security group with caller-defined, opt-in ingress "
         "rules and an allow-all egress rule",
         "Terraform + AWS provider (aws_security_group, aws_security_group_rule)"],
        ["modules/iam-role", "IAM role supporting either a standard service trust policy (EC2, "
         "Lambda, etc.) or EKS IRSA (OIDC) trust, with managed/inline policy attachment",
         "Terraform + AWS provider (aws_iam_role, aws_iam_policy_document, aws_iam_role_policy)"],
        ["examples/*", "Runnable, minimal root configurations demonstrating one module each "
         "(rds-mysql, s3-secure, iam-irsa)",
         "Terraform root configurations calling the modules above"],
        [".github/workflows/validate-modules.yaml", "CI gate: format check, terraform validate, "
         "and tflint, run per module on every push/PR to main",
         "GitHub Actions, hashicorp/setup-terraform, terraform-linters/setup-tflint"],
    ],
)

doc.add_heading2("3.1 Component descriptions")
doc.add_heading3("vpc")
doc.add_paragraph(
    "Builds the network layer other modules (rds, security-group, and any "
    "consumer-provisioned compute) attach to: a VPC, an internet gateway, one "
    "public and one private subnet per supplied availability zone, one NAT "
    "gateway per public subnet (each with its own Elastic IP), and public/"
    "private route tables with their associations. Public subnets are tagged "
    "kubernetes.io/role/elb = 1 and private subnets kubernetes.io/role/"
    "internal-elb = 1 and karpenter.sh/discovery = <cluster_name>, so the "
    "module is usable as-is under an EKS cluster with Karpenter node "
    "autoscaling, even though this repository does not itself provision EKS."
)
doc.add_heading3("rds")
doc.add_paragraph(
    "Provisions a single RDS instance (MySQL by default, but engine and "
    "engine_version are variables) along with its own dedicated security "
    "group scoped to a caller-supplied CIDR list and port, a DB subnet group "
    "built from caller-supplied subnet IDs, and an IAM role + policy "
    "attachment for RDS enhanced monitoring. Storage encryption, public "
    "accessibility, Performance Insights, and enhanced monitoring are not "
    "optional — they are hardcoded on."
)
doc.add_heading3("s3-bucket")
doc.add_paragraph(
    "Provisions one S3 bucket with versioning (togglable), server-side "
    "encryption (always on — SSE-KMS if a key ARN is supplied, otherwise "
    "SSE-S3/AES256), an unconditional public-access-block resource, and "
    "optional lifecycle rules (transition/expiration) and access logging to a "
    "second bucket."
)
doc.add_heading3("security-group")
doc.add_paragraph(
    "Provisions a standalone security group whose ingress rules are entirely "
    "caller-supplied via a list of rule objects (empty by default — no open "
    "ports unless requested) and whose egress is a single allow-all rule, "
    "matching default AWS security group behavior. Intended for consumer "
    "resources (e.g. an application's own EC2 instances or load balancers) "
    "that need a security group independent of the one rds creates for itself."
)
doc.add_heading3("iam-role")
doc.add_paragraph(
    "Provisions a single IAM role whose trust policy is selected automatically: "
    "if both oidc_provider_arn and service_account_name are supplied, it builds "
    "an EKS IRSA (OIDC federation) trust policy scoped to that provider and "
    "Kubernetes service account/namespace; otherwise it builds a standard AWS "
    "service-principal trust policy from trusted_service (e.g. "
    "ec2.amazonaws.com or lambda.amazonaws.com). Managed policy ARNs and a "
    "single inline policy document can both be attached."
)

# 4. End-to-end functional workflow
doc.add_heading1("4. End-to-end functional workflow")
doc.add_paragraph(
    "There is no runtime request flow in a module library — the relevant "
    "'workflow' is how a consumer composes modules together at plan/apply time "
    "so that one module's outputs feed another module's inputs. The typical "
    "composition order for a full environment is:"
)
doc.add_figure_placeholder(
    "Figure 1: Typical module composition/dependency order — vpc -> "
    "security-group -> rds / consumer compute -> s3-bucket / iam-role"
)
doc.add_bullets([
    "1. vpc is applied first. It has no dependency on any other module in this "
    "repository and produces vpc_id, public_subnet_ids, and private_subnet_ids.",
    "2. security-group is applied next, taking vpc.vpc_id as its vpc_id input, "
    "to create any additional security groups the consumer's own compute needs "
    "(rds provisions its own internal security group and does not need this "
    "module).",
    "3. rds is applied using vpc.vpc_id and vpc.private_subnet_ids (typically) "
    "as its vpc_id and subnet_ids inputs, and the consumer's own or the "
    "security-group module's output as part of allowed_cidr_blocks.",
    "4. s3-bucket and iam-role have no dependency on vpc, rds, or each other — "
    "they can be applied in any order, independently, at any point. iam-role "
    "is commonly wired to reference an s3-bucket output (e.g. an inline policy "
    "Resource ARN built from bucket_arn) when granting a role access to a "
    "specific bucket, as shown in the iam-irsa example.",
])
doc.add_paragraph(
    "Because modules do not call each other internally, this ordering is a "
    "convention enforced by the consumer's own module block wiring and "
    "Terraform's implicit dependency graph (derived from output-to-input "
    "references), not by anything inside this repository."
)

# 5. Module-wise design overview
doc.add_heading1("5. Module-wise design overview")

doc.add_heading2("5.1 vpc")
doc.add_paragraph(
    "Design choice: subnet count and layout are driven entirely by the length "
    "of the public_subnet_cidrs / private_subnet_cidrs / availability_zones "
    "lists (via Terraform count), rather than a fixed 2-AZ or 3-AZ assumption. "
    "This means the module scales to however many AZs a consumer passes in, "
    "but also means the three lists must be kept the same length and "
    "correctly ordered by the caller — the module performs no cross-checking "
    "between them beyond what count naturally enforces (a mismatched length "
    "will fail at plan time with an index error rather than a clear validation "
    "message)."
)
doc.add_paragraph(
    "Design choice: one NAT gateway per public subnet (not a single shared NAT "
    "gateway) is provisioned, trading a small cost increase for AZ-independent "
    "egress — a private subnet's outbound traffic does not cross an "
    "availability zone boundary through a single NAT gateway."
)

doc.add_heading2("5.2 rds")
doc.add_paragraph(
    "Design choice: the module owns and creates its own security group rather "
    "than accepting one as an input. This keeps the module self-contained (a "
    "consumer only needs to pass allowed_cidr_blocks and a port) at the cost "
    "of flexibility — a consumer cannot attach an externally managed security "
    "group to the instance."
)
doc.add_paragraph(
    "Design choice: several production-safety settings are hardcoded rather "
    "than exposed as variables — storage_encrypted, publicly_accessible, "
    "Performance Insights, and enhanced monitoring are always on. "
    "deletion_protection defaults to true and skip_final_snapshot defaults to "
    "false, so the default posture favors not losing data over convenience "
    "during throwaway testing; both examples/rds-mysql and a consumer's own "
    "dev environment must explicitly opt out (deletion_protection = false, "
    "skip_final_snapshot = true) to get disposable-instance behavior."
)

doc.add_heading2("5.3 s3-bucket")
doc.add_paragraph(
    "Design choice: aws_s3_bucket_public_access_block is created "
    "unconditionally with all four blocking flags hardcoded true — there is no "
    "variable to disable it. This is a deliberate 'secure by construction' "
    "choice: a consumer who genuinely needs a public bucket (e.g. static "
    "website hosting) cannot do so through this module and must provision that "
    "bucket outside it."
)
doc.add_paragraph(
    "Design choice: encryption is similarly non-optional — the only choice "
    "exposed is which algorithm (SSE-KMS vs SSE-S3), selected implicitly by "
    "whether kms_key_arn is null, not whether encryption happens at all. "
    "Lifecycle rules are modeled as a list(object(...)) with a dynamic block, "
    "so a consumer can supply zero, one, or many transition/expiration rules "
    "without the module needing a variable per rule."
)

doc.add_heading2("5.4 security-group")
doc.add_paragraph(
    "Design choice: ingress_rules defaults to an empty list, and each rule is "
    "applied as its own aws_security_group_rule resource via for_each (keyed "
    "by list index) rather than inline blocks on the security group resource "
    "itself. This means adding/removing a rule in the middle of the list only "
    "affects that rule's resource address in state (index-keyed for_each), and "
    "the security group resource carries create_before_destroy in its "
    "lifecycle block so replacing the group doesn't leave dependents briefly "
    "without a security group."
)
doc.add_paragraph(
    "Design choice: each rule object supports either cidr_blocks or "
    "source_sg_id (both optional), letting a single rule shape express both "
    "CIDR-based and security-group-referencing ingress without two separate "
    "variables."
)

doc.add_heading2("5.5 iam-role")
doc.add_paragraph(
    "Design choice: the module infers which trust policy to build from which "
    "variables are set (a local.is_irsa boolean gated on oidc_provider_arn != "
    "null && service_account_name != null) rather than requiring an explicit "
    "'mode' variable. This keeps the common case (service-principal trust) to "
    "a single required variable, at the cost of the trust-policy choice being "
    "implicit rather than declared."
)
doc.add_paragraph(
    "Design choice: managed policy attachment uses for_each over a set of "
    "ARNs (so any number, including zero, can be attached idempotently), while "
    "the inline policy is a single optional document gated by count — a "
    "consumer needing more than one inline policy must compose them into one "
    "document before passing it in."
)

# 6. State & configuration model
doc.add_heading1("6. State & configuration model")
doc.add_paragraph(
    "This repository does not ship or prescribe a remote state backend "
    "module, and none of the example root configurations under examples/ "
    "declare a backend block — each example is run with Terraform's default "
    "local backend (terraform.tfstate written to the working directory), "
    "consistent with them being minimal, self-contained demonstrations rather "
    "than production root configurations. The repository's .gitignore "
    "excludes *.tfstate files, so state is never expected to be committed."
)
doc.add_paragraph(
    "A consumer adopting these modules in a real environment is expected to "
    "configure their own remote backend (e.g. an S3 bucket with DynamoDB "
    "locking, or Terraform Cloud) in their own root configuration's terraform "
    "block — this is intentionally left outside the module library's "
    "responsibility, since backend configuration is environment-specific and "
    "cannot itself be parameterized inside a child module (Terraform does not "
    "allow a module to configure its caller's backend)."
)
doc.add_paragraph(
    "Variable/output contract philosophy: every module follows the same "
    "shape — a variables.tf exposing only what a caller must decide (naming, "
    "network placement, and a small number of tunable knobs), an outputs.tf "
    "exposing only the identifiers a caller is likely to need to wire into "
    "another module (IDs, ARNs, endpoints), and a tags variable (default {}) "
    "present on every module for consistent, caller-controlled resource "
    "tagging. Security-relevant behavior (encryption, public access blocking) "
    "is deliberately kept out of the variable surface where the design intent "
    "is 'always on' rather than 'configurable', per Section 9."
)

# 7. Technology stack
doc.add_heading1("7. Technology stack")
doc.add_table(
    headers=["Layer", "Technology", "Notes"],
    rows=[
        ["IaC language", "Terraform >= 1.7.0", "Declared per-module in each module's versions.tf, and repeated in the root README"],
        ["Cloud provider", "AWS provider (hashicorp/aws) ~> 6.0", "No module hardcodes a provider block or credentials — consumers supply their own provider configuration"],
        ["CI", "GitHub Actions (.github/workflows/validate-modules.yaml)", "Matrix job across all 5 modules: terraform fmt -check, terraform init -backend=false, terraform validate"],
        ["Linting", "tflint (terraform-linters/setup-tflint)", "Run per module in the same CI matrix, after terraform validate"],
        ["Version control", "Git / GitHub (ravishekharg account, Darviq Systems brand)", "Source referenced by consumers as github.com/ravishekharg/Terraform-Aws-Modules//modules/<name>"],
    ],
)

# 8. Deployment architecture
doc.add_heading1("8. Deployment architecture")
doc.add_paragraph(
    "There is no single 'deployment' of this repository — it is consumed by "
    "reference, not deployed itself. The closest equivalent to a deployment "
    "diagram is how a consumer's root configuration typically invokes these "
    "modules together for a real environment (e.g. a dev or prod workspace)."
)
doc.add_figure_placeholder(
    "Figure 2: Example consumer root configuration wiring vpc -> rds and "
    "vpc -> security-group, with s3-bucket and iam-role attached independently"
)
doc.add_paragraph(
    "The repository's own examples/ directory shows this pattern at module "
    "granularity rather than as a single combined environment: "
    "examples/rds-mysql provisions the rds module directly against literal "
    "(non-vpc-module) VPC/subnet IDs, examples/s3-secure provisions the "
    "s3-bucket module with a lifecycle rule, and examples/iam-irsa provisions "
    "the iam-role module against a literal EKS OIDC provider ARN for an IRSA "
    "service account. Each example has its own versions.tf and "
    ".terraform.lock.hcl and is runnable standalone with terraform init / "
    "terraform plan, as documented in the root README's Usage section. None "
    "of the three examples currently compose the vpc module together with "
    "rds/security-group in a single example, so a consumer wiring multiple "
    "modules together (as described in Section 4) is following a documented "
    "convention rather than copying a ready-made combined example from this "
    "repository."
)

# 9. Security design
doc.add_heading1("9. Security design")
doc.add_table(
    headers=["Module", "Security-relevant default"],
    rows=[
        ["s3-bucket", "aws_s3_bucket_public_access_block is created unconditionally with all "
         "four flags (block_public_acls, block_public_policy, ignore_public_acls, "
         "restrict_public_buckets) set true — not exposed as a variable, so there "
         "is no way to provision a public bucket through this module"],
        ["s3-bucket", "Server-side encryption is always applied: aws:kms when kms_key_arn is "
         "set, otherwise AES256 (SSE-S3) — the bucket is never left unencrypted"],
        ["rds", "storage_encrypted = true and publicly_accessible = false are hardcoded "
         "(not variables) — every instance this module creates is encrypted at "
         "rest and not publicly reachable"],
        ["rds", "The instance's own security group only allows inbound traffic from "
         "var.allowed_cidr_blocks on var.port; there is no default-open ingress "
         "rule"],
        ["rds", "deletion_protection defaults to true, so accidental terraform destroy "
         "is blocked unless a consumer explicitly opts out"],
        ["security-group", "ingress_rules defaults to an empty list — no port is open on a new "
         "security group unless the consumer explicitly adds a rule; egress is "
         "allow-all by default, matching standard AWS security group behavior "
         "(documented in the module's README as an explicit, not accidental, "
         "choice)"],
        ["iam-role", "Trust policies are scoped, not wildcarded: the IRSA trust policy "
         "condition-restricts sts:AssumeRoleWithWebIdentity to a specific "
         "Kubernetes namespace/service-account subject and the sts.amazonaws.com "
         "audience; the service-principal trust policy is scoped to exactly the "
         "trusted_service string supplied, with no default wildcard principal"],
        ["iam-role", "No managed policy ARNs or inline policy are attached unless the "
         "consumer supplies them (both default to empty/null) — the module does "
         "not grant any permissions beyond the trust (assume-role) policy on its "
         "own"],
        ["All modules", "Credentials are never hardcoded or read from a checked-in file — the "
         "AWS provider is configured entirely by the consumer's own environment "
         "(env vars, profile, or assumed role), and the root README explicitly "
         "warns never to commit *.tfvars with real credentials or *.tfstate "
         "files (both are .gitignored)"],
    ],
)

# 10. Non-functional requirements
doc.add_heading1("10. Non-functional requirements")
doc.add_table(
    headers=["Attribute", "Target / approach"],
    rows=[
        ["Reusability", "Each module is self-contained (own variables/outputs/versions) and "
         "has no dependency on any other module in this repository, so any "
         "subset can be adopted independently"],
        ["Consistency", "Every module exposes a tags variable (default {}) and applies it via "
         "merge() alongside a computed Name tag, so tagging behavior is uniform "
         "across the library"],
        ["Versioning approach", "Terraform and AWS provider version constraints (>= 1.7.0, ~> 6.0) are "
         "declared per-module in each module's own versions.tf, so a module can "
         "be pinned/upgraded independently of the others"],
        ["Backward compatibility", "No formal semantic-versioning/tagging scheme (e.g. git tags per module "
         "release) is present in the repository today; consumers currently "
         "reference modules by path against the default branch rather than a "
         "pinned release tag — see Section 12"],
        ["Quality gating", "CI (validate-modules.yaml) runs terraform fmt -check, terraform "
         "validate, and tflint against every module on every push/PR to main, "
         "so a formatting or syntax regression cannot merge silently"],
        ["Auditability", "Each module ships its own README.md documenting inputs, outputs, and "
         "security defaults in the same repository location as the code, so "
         "documentation cannot drift far from implementation without being "
         "immediately visible in the same PR diff"],
    ],
)

# 11. Assumptions & constraints
doc.add_heading1("11. Assumptions & constraints")
doc.add_bullets([
    "Consumers provide their own AWS provider configuration (credentials, "
    "region, default tags) — no module declares a provider block.",
    "Consumers provide their own remote state backend if one is desired; "
    "this repository's examples run against local state only (Section 6).",
    "The rds module assumes the caller already has a VPC and subnet IDs "
    "available (typically from the vpc module's outputs, but the module "
    "accepts any valid vpc_id/subnet_ids, as examples/rds-mysql demonstrates "
    "with literal placeholder IDs).",
    "The vpc module's public/private subnet Kubernetes tags "
    "(kubernetes.io/role/elb, karpenter.sh/discovery, etc.) assume an EKS "
    "context; they are harmless but unused if the consumer is not running "
    "EKS/Karpenter.",
    "All five modules require AWS provider ~> 6.0 and Terraform >= 1.7.0 — "
    "older provider/Terraform versions are not tested by CI and are not "
    "guaranteed to work.",
    "The rds module's password variable is marked sensitive but still "
    "requires a real value at plan/apply time; the module does not integrate "
    "with a secrets manager itself, it only documents that the caller should "
    "source the value from one.",
    "No module in this repository provisions a standalone EC2 instance, "
    "Auto Scaling group, or EKS cluster — compute is entirely the consumer's "
    "responsibility; this repository provides the network (vpc), the "
    "database (rds), the storage (s3-bucket), and the access-control "
    "primitives (security-group, iam-role) that compute would sit alongside.",
])

# 12. Future enhancements
doc.add_heading1("12. Future enhancements")
doc.add_bullets([
    "A pinned release/versioning scheme (e.g. git tags per module version, "
    "referenced by consumers via ?ref=vX.Y.Z) — today the README's example "
    "source reference has no ref pin, so consumers on the default branch "
    "pick up changes without an explicit upgrade step.",
    "A standalone compute module (EC2 instance or Auto Scaling group with a "
    "launch template) to complement iam-role's existing EC2 trust-policy "
    "support and vpc's subnet layout, closing the gap between this "
    "repository's actual module set and its one-line description.",
    "A remote-state backend module or documented backend pattern (S3 + "
    "DynamoDB lock table), since Section 6 shows the repository currently "
    "leaves this entirely to the consumer.",
    "Variable validation blocks (Terraform's validation {} inside "
    "variable) for cross-field constraints the modules currently rely on "
    "implicit behavior for — for example, the vpc module's three CIDR/AZ "
    "lists having matching lengths (Section 5.1) is not currently enforced "
    "and would fail with an unclear index error rather than a validation "
    "message.",
    "A combined, multi-module example under examples/ (vpc + security-group "
    "+ rds wired together end to end) — the three current examples each "
    "demonstrate one module in isolation, so the composition pattern "
    "described in Section 4 is documented in prose but not yet demonstrated "
    "as runnable code in this repository.",
    "Automated unit/contract testing (e.g. Terratest or terraform test) "
    "beyond the current fmt/validate/tflint CI gate, which checks syntax and "
    "style but not actual provisioned-resource behavior.",
])

# 13. Appendix
doc.add_heading1("13. Appendix")
doc.add_heading2("13.1 References")
doc.add_bullets([
    "Repository README: D:/Projects/Cloud/Darviq-Terraform/README.md",
    "Per-module READMEs: modules/vpc/README.md, modules/rds/README.md, "
    "modules/s3-bucket/README.md, modules/security-group/README.md, "
    "modules/iam-role/README.md",
    "CI workflow: .github/workflows/validate-modules.yaml",
    "Example root configurations: examples/rds-mysql/main.tf, "
    "examples/s3-secure/main.tf, examples/iam-irsa/main.tf",
    "Companion document: Darviq_Terraform_Low_Level_Design.docx (this "
    "repository's LLD, Docs/ folder)",
])

doc.add_heading2("13.2 Change history")
doc.add_table(
    headers=["Version", "Date", "Description"],
    rows=[[VERSION, DATE, "Initial high-level design document"]],
)

doc.save("Darviq_Terraform_High_Level_Design.docx")
print("HLD saved.")
