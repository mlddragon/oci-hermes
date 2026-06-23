resource "oci_core_vcn" "hermes" {
  compartment_id = var.compartment_ocid
  cidr_block     = "10.40.0.0/16"
  display_name   = "${local.name_prefix}-vcn"
  dns_label      = "hermesfree"
  freeform_tags  = var.freeform_tags
}

resource "oci_core_internet_gateway" "hermes" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.hermes.id
  display_name   = "${local.name_prefix}-igw"
  enabled        = true
  freeform_tags  = var.freeform_tags
}

resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.hermes.id
  display_name   = "${local.name_prefix}-public-routes"
  freeform_tags  = var.freeform_tags

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.hermes.id
  }
}

resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.hermes.id
  display_name   = "${local.name_prefix}-public-security"
  freeform_tags  = var.freeform_tags

  ingress_security_rules {
    protocol = local.tcp_protocol
    source   = var.ssh_allowed_cidr

    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = local.tcp_protocol
    source   = "0.0.0.0/0"

    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = local.tcp_protocol
    source   = "0.0.0.0/0"

    tcp_options {
      min = 443
      max = 443
    }
  }

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.hermes.id
  cidr_block                 = "10.40.10.0/24"
  display_name               = "${local.name_prefix}-public-subnet"
  dns_label                  = "public"
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.public.id]
  prohibit_public_ip_on_vnic = false
  freeform_tags              = var.freeform_tags
}
