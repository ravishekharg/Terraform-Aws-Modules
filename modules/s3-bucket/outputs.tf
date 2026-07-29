output "bucket_id" {
  value       = aws_s3_bucket.main.id
  description = "ID of the created S3 bucket"
}

output "bucket_arn" {
  value       = aws_s3_bucket.main.arn
  description = "ARN of the created S3 bucket"
}

output "bucket_name" {
  value       = aws_s3_bucket.main.bucket
  description = "Name of the created S3 bucket"
}
