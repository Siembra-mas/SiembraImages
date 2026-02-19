variable "aws_account_id" {
  type = string
}

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

# Creamos el almacén de usuarios (User Pool)
resource "aws_cognito_user_pool" "siembra_users" {
  name = "siembrasnap-pool"

  # El correo será el identificador principal
  username_attributes = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length = 8
    require_numbers = true
    require_symbols = false
  }
}

# Creamos el "Cliente" para que tu App de Render pueda hablar con Cognito
resource "aws_cognito_user_pool_client" "client" {
  name         = "siembrasnap-app-client"
  user_pool_id = aws_cognito_user_pool.siembra_users.id
  
  explicit_auth_flows = ["USER_PASSWORD_AUTH"]
}