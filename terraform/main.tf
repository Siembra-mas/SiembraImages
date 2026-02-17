# Solo el Bucket
resource "aws_s3_bucket" "siembrasnap_storage" {
  bucket = "siembrasnap-nando-2026"
  force_destroy = true 
}

# Bloqueo de seguridad
resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.siembrasnap_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# App Service
resource "aws_apprunner_service" "siembrasnap_service" {
  service_name = "siembrasnap-service"

  source_configuration {
    image_repository {
      image_identifier      = "959284555099.dkr.ecr.us-east-1.amazonaws.com/siembrasnap-repo:latest"
      image_repository_type = "ECR"
      image_configuration {
        port = "5000"
        runtime_environment_variables = {
          "AWS_REGION" = "us-east-1"
          # Nota: Las llaves secretas es mejor ponerlas en el dashboard por seguridad
        }
      }
    }
    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu    = "0.25 vCPU"
    memory = "0.5 GB"
  }
}