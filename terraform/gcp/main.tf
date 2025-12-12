terraform {
  required_version = ">= 1.3"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_secret_manager_secret" "openai" {
  secret_id = "email-assistant-openai"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "openai_v" {
  secret      = google_secret_manager_secret.openai.id
  secret_data = var.openai_api_key
}

resource "google_secret_manager_secret" "google_client_id" {
  secret_id = "email-assistant-google-client-id"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_client_id_v" {
  secret      = google_secret_manager_secret.google_client_id.id
  secret_data = var.google_client_id
}

resource "google_secret_manager_secret" "google_client_secret" {
  secret_id = "email-assistant-google-client-secret"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_client_secret_v" {
  secret      = google_secret_manager_secret.google_client_secret.id
  secret_data = var.google_client_secret
}

resource "google_secret_manager_secret" "database_url" {
  secret_id = "email-assistant-database-url"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "database_url_v" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = var.database_url
}

resource "google_secret_manager_secret" "allowed_origins" {
  secret_id = "email-assistant-allowed-origins"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "allowed_origins_v" {
  secret      = google_secret_manager_secret.allowed_origins.id
  secret_data = var.allowed_origins
}

resource "google_container_cluster" "primary" {
  name     = "email-assistant"
  location = var.region
  remove_default_node_pool = true
  initial_node_count       = 1
  network    = var.network
  subnetwork = var.subnetwork
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-nodes"
  cluster    = google_container_cluster.primary.name
  location   = var.region
  node_count = 2

  node_config {
    machine_type = "e2-standard-2"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

provider "kubernetes" {
  host                   = "https://${google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.current.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
}

data "google_client_config" "current" {}

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

variable "project" { type = string }
variable "region" { type = string }
variable "zone" { type = string }
variable "network" { type = string }
variable "subnetwork" { type = string }
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
