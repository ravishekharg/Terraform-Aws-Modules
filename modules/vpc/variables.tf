variable "project_name" {
  type        = string
  description = "Project name for resource naming"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name for subnet tags"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the VPC"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for the public subnets, one per availability zone"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for the private subnets, one per availability zone"
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones to spread the public/private subnets across"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags applied to all resources created by this module"
}
