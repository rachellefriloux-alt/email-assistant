terraform {
  required_version = ">= 1.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

resource "aws_secretsmanager_secret" "openai" {
  name = "email-assistant/openai"
}

resource "aws_secretsmanager_secret_version" "openai_v" {
  secret_id     = aws_secretsmanager_secret.openai.id
  secret_string = var.openai_api_key
}

resource "aws_secretsmanager_secret" "google_client_id" {
  name = "email-assistant/google-client-id"
}

resource "aws_secretsmanager_secret_version" "google_client_id_v" {
  secret_id     = aws_secretsmanager_secret.google_client_id.id
  secret_string = var.google_client_id
}

resource "aws_secretsmanager_secret" "google_client_secret" {
  name = "email-assistant/google-client-secret"
}

resource "aws_secretsmanager_secret_version" "google_client_secret_v" {
  secret_id     = aws_secretsmanager_secret.google_client_secret.id
  secret_string = var.google_client_secret
}

resource "aws_secretsmanager_secret" "database_url" {
  name = "email-assistant/database-url"
}

resource "aws_secretsmanager_secret_version" "database_url_v" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = var.database_url
}

resource "aws_secretsmanager_secret" "allowed_origins" {
  name = "email-assistant/allowed-origins"
}

resource "aws_secretsmanager_secret_version" "allowed_origins_v" {
  secret_id     = aws_secretsmanager_secret.allowed_origins.id
  secret_string = var.allowed_origins
}

resource "aws_eks_cluster" "this" {
  name     = "email-assistant"
  role_arn = var.eks_role_arn

  vpc_config {
    subnet_ids = var.private_subnet_ids
  }
}

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "email-assistant-ng"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = 2
    max_size     = 5
    min_size     = 2
  }
  instance_types = ["t3.medium"]
}

provider "kubernetes" {
  host                   = aws_eks_cluster.this.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.this.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.this.token
}

data "aws_eks_cluster_auth" "this" {
  name = aws_eks_cluster.this.name
}

resource "kubernetes_namespace" "app" {
  metadata { name = var.namespace }
}

resource "kubernetes_secret" "app" {
  metadata {
    name      = "email-assistant-secret"
    namespace = kubernetes_namespace.app.metadata[0].name
  }
  data = {
    OPENAI_API_KEY       = base64encode(var.openai_api_key)
    GOOGLE_CLIENT_ID     = base64encode(var.google_client_id)
    GOOGLE_CLIENT_SECRET = base64encode(var.google_client_secret)
    DATABASE_URL         = base64encode(var.database_url)
    ALLOWED_ORIGINS      = base64encode(var.allowed_origins)
  }
}

resource "kubernetes_config_map" "app" {
  metadata {
    name      = "email-assistant-config"
    namespace = kubernetes_namespace.app.metadata[0].name
  }
  data = {
    VITE_API_BASE = var.vite_api_base
  }
}

variable "region" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "eks_role_arn" { type = string }
variable "node_role_arn" { type = string }
variable "namespace" {
  type    = string
  default = "email-assistant"
}

variable "openai_api_key" { type = string }
variable "google_client_id" { type = string }
variable "google_client_secret" { type = string }
variable "database_url" { type = string }
variable "allowed_origins" { type = string }

variable "vite_api_base" {
  type    = string
  default = "http://localhost:8000"
}
