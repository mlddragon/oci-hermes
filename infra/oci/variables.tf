variable "region" {
  description = "OCI region for the deployer-owned Hermes deployment."
  type        = string
}

variable "compartment_ocid" {
  description = "Deployer-owned OCI compartment OCID. Resolved locally by hermesctl before apply."
  type        = string
}

variable "availability_domain" {
  description = "Optional availability domain. Leave blank to use the first available AD."
  type        = string
  default     = ""
}

variable "ssh_public_key_path" {
  description = "Path to the deployer's dedicated Hermes OCI SSH public key."
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "Narrow IPv4 CIDR allowed to SSH to the instance."
  type        = string
}

variable "shape" {
  description = "Always Free A1 Flex shape."
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "ocpus" {
  description = "A1 Flex OCPU count. v1 Always Free target is 2."
  type        = number
  default     = 2
}

variable "memory_gb" {
  description = "A1 Flex memory in GB. v1 Always Free target is 12."
  type        = number
  default     = 12
}

variable "boot_volume_gb" {
  description = "Boot volume size in GB."
  type        = number
  default     = 150
}

variable "freeform_tags" {
  description = "Non-secret tags for deployer-owned OCI resources."
  type        = map(string)
  default = {
    project = "oci-hermes"
  }
}
