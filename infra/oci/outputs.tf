output "instance_ocid" {
  description = "OCI instance OCID. Treat as deployment-local metadata."
  value       = oci_core_instance.hermes.id
  sensitive   = true
}

output "public_ip" {
  description = "Assigned public IP for DuckDNS. Do not commit this value."
  value       = oci_core_instance.hermes.public_ip
}

output "ssh_command" {
  description = "Convenience SSH command for the deployer."
  value       = "ssh ubuntu@${oci_core_instance.hermes.public_ip}"
}
