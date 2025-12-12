provider "google" {
  project = "your-gcp-project"
  region  = "us-central1"
}

resource "google_compute_instance" "email_assistant" {
  name         = "email-assistant"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }
}
