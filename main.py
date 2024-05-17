import string
import random
import json

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

IN_CLUSTER = "IN_CLUSTER"
OUT_CLUSTER = "OUT_CLUSTER"

state = {
  "value": OUT_CLUSTER,
  "nested_par": 0,
  "curr_cluster": -1
}

clusters = []
advanced_clusters = []
curr_cluster_stack = [] # {attr_name: "", content: {}}

def read_terraform_file(filename: str):
  """
  Reads a Terraform file and returns a dictionary of resources.

  Args:
      filename: The path to the Terraform file.

  Returns:
      A dictionary where keys are resource types and values are lists of resource names.
  """
  with open(filename, "r") as f:
    i = 0
    for i, line in enumerate(f):
      state_to_function[state["value"]](line)


def look_for_cluster(line: str):
  if line.strip().startswith('resource "mongodbatlas_cluster"'):
    # Extract resource type and name
    parts = line.split()[1:]
    resource_name = parts[1]

    state["curr_cluster"] += 1
    curr_cluster_stack.append({"attr_name": "__root__", "content": {}})
    curr_cluster_stack[-1]["resource_name"] = resource_name
    state["value"] = IN_CLUSTER


def look_for_fields(line: str):
  line = line.strip()
  if line == "" or line.startswith("#"):
    return
  if line.startswith("}") and len(curr_cluster_stack) == 1:
    state["value"] = OUT_CLUSTER
    clusters.append(curr_cluster_stack.pop())
    return
  if line.startswith("}") and len(curr_cluster_stack) > 1:
    complex_attribute = curr_cluster_stack.pop()
    if curr_cluster_stack[-1]["content"].get(complex_attribute["attr_name"]) == None:
      curr_cluster_stack[-1]["content"][complex_attribute["attr_name"]] = []
    curr_cluster_stack[-1]["content"][complex_attribute["attr_name"]].append(complex_attribute["content"])
    return
  
  parts = line.split(" ")
  attribute = parts[0]
  rest = "".join(parts[1:])
  if rest.strip().startswith("{"):
    curr_cluster_stack.append({"attr_name": attribute, "content": {}})
    return
  value = rest.split("=")[1:]
  curr_cluster_stack[-1]["content"][attribute] = value[0]

state_to_function = {
  OUT_CLUSTER: look_for_cluster,
  IN_CLUSTER: look_for_fields,
}

def project_id(cluster):
  return "project_id = {0}".format(cluster.get('project_id'))

def name(cluster):
  return "name = {0}".format(cluster.get('name'))

def cluster_type(cluster):
  if cluster.get('cluster_type') is None:
    return ""  
  return "cluster_type = {0}".format(cluster.get('cluster_type'))

def backup_enabled(cluster):
  if cluster.get('cloud_backup') is None:
    return ""
  return "cloud_backup = {0}".format(cluster.get('cloud_backup')) # https://registry.terraform.io/providers/mongodb/mongodbatlas/latest/docs/resources/cluster#backup_enabled backup_enabled on cluster refers to legacy backup

def retain_backups_enabled(cluster):
  if cluster.get('retain_backups_enabled') is None:
    return ""
  return "retain_backups_enabled = {0}".format(cluster.get('retain_backups_enabled'))

def bi_connector_config(cluster):
  if cluster.get('bi_connector_config') is None:
    return ""
  return "bi_connector_config = {0}".format(cluster.get('bi_connector_config'))

def disk_size_gb(cluster):
  if cluster.get('disk_size_gb') is None:
    return ""  
  return "disk_size_gb = {0}".format(cluster.get('disk_size_gb'))

def encryption_at_rest_provider(cluster):
  if cluster.get('encryption_at_rest_provider') is None:
    return ""
  return "encryption_at_rest_provider = {0}".format(cluster.get('encryption_at_rest_provider'))

def tags(cluster):
  if cluster.get('tags') is None:
    return ""  
  return "tags = {0}".format(cluster.get('tags'))

def labels(cluster):
  if cluster.get('labels') is None:
    return ""
  return "labels = {0}".format(cluster.get('labels'))

def mongo_db_major_version(cluster):
  if cluster.get('mongo_db_major_version') is None:
    return ""
  return "mongo_db_major_version = {0}".format(cluster.get('mongo_db_major_version'))

def pit_enabled(cluster):
  if cluster.get('pit_enabled') is None:
    return ""
  return "pit_enabled = {0}".format(cluster.get('pit_enabled'))

def termination_protection_enabled(cluster):
  if cluster.get('termination_protection_enabled') is None:
    return ""
  return "termination_protection_enabled = {0}".format(cluster.get('termination_protection_enabled'))

def version_release_system(cluster):
  if cluster.get('version_release_system') is None:
    return ""
  return "version_release_system = {0}".format(cluster.get('version_release_system'))

def paused(cluster):
  if cluster.get('paused') is None:
    return ""
  return "paused = {0}".format(cluster.get('paused'))

def timeouts(cluster):
  if cluster.get('timeouts') is None:
    return ""
  return "timeouts = {0}".format(cluster.get('timeouts'))

def accept_data_risks_and_force_replica_set_reconfig(cluster):
  if cluster.get('accept_data_risks_and_force_replica_set_reconfig') is None:
    return ""
  return "accept_data_risks_and_force_replica_set_reconfig = {0}".format(cluster.get('accept_data_risks_and_force_replica_set_reconfig'))

def advanced_configuration(cluster):
  if cluster.get('advanced_configuration') is None:
    return ""
  return "advanced_configuration = {0}".format(cluster.get('advanced_configuration'))

def replication_specs(cluster):
  # print(cluster)
  advanced_replication_specs = []
  replication_specs = cluster.get("replication_specs")
  if replication_specs is None:
    return []

  for replication_spec in replication_specs:
    advanced_replication_spec = {}
    advanced_replication_spec["zone_name"] = replication_spec.get("zone_name")
    advanced_replication_spec["num_shards"] = replication_spec.get("num_shards")
    if replication_spec.get("regions_config") != None:
      advanced_region_configs = []
      regions_config = replication_spec.get("regions_config")
      for region_config in regions_config:
        advanced_region_config = {}
        advanced_region_config["priority"] = region_config.get("priority")
        advanced_region_config["region_name"] = region_config.get("region_name")
        advanced_region_config["provider_name"] = cluster.get("provider_name")
        electable_specs_tf_config = """"""
        if region_config.get("electable_nodes") != None:
          advanced_region_config["electable_specs"] = {}
          advanced_region_config["electable_specs"]["instance_size"] = cluster.get("provider_instance_size_name")
          advanced_region_config["electable_specs"]["node_count"] = region_config.get("electable_nodes")
          disk_iops = ""
          if cluster.get("provider_disk_iops") != None:
            disk_iops = "disk_iops = {0}".format(cluster.get("provider_disk_iops"))
          electable_specs_tf_config = """
      electable_specs {{
        instance_size = {instance_size}
        node_count = {node_count}
        {disk_iops}
      }}
      """.format(
              instance_size=advanced_region_config["electable_specs"]["instance_size"],
              node_count=advanced_region_config["electable_specs"]["node_count"],
              disk_iops=disk_iops,
            )

        read_only_specs_tf_config = """"""
        if region_config.get("read_only_nodes") != None:
          advanced_region_config["read_only_specs"] = {}
          advanced_region_config["read_only_specs"]["instance_size"] = cluster.get("provider_instance_size_name")
          advanced_region_config["read_only_specs"]["node_count"] = region_config.get("read_only_nodes")
          disk_iops = ""
          if cluster.get("provider_disk_iops") != None:
            disk_iops = "disk_iops = {0}".format(cluster.get("provider_disk_iops"))
          read_only_specs_tf_config = """
      read_only_specs {{
        instance_size = {instance_size}
        node_count = {node_count}
        {disk_iops}
      }}
      """.format(
              instance_size=advanced_region_config["read_only_specs"]["instance_size"],
              node_count=advanced_region_config["read_only_specs"]["node_count"],
              disk_iops=disk_iops,
            )

        analytics_specs_tf_config = """"""
        if region_config.get("analytics_nodes") != None:
          advanced_region_config["analytics_specs"] = {}
          advanced_region_config["analytics_specs"]["instance_size"] = cluster.get("provider_instance_size_name")
          advanced_region_config["analytics_specs"]["node_count"] = region_config.get("analytics_nodes")
          disk_iops = ""
          if cluster.get("provider_disk_iops") != None:
            disk_iops = "disk_iops = {0}".format(cluster.get("provider_disk_iops"))          
          analytics_specs_tf_config = """
      analytics_specs {{
        instance_size = {instance_size}
        node_count = {node_count}
        {disk_iops}
      }}
      """.format(
              instance_size=advanced_region_config["analytics_specs"]["instance_size"],
              node_count=advanced_region_config["analytics_specs"]["node_count"],
              disk_iops=disk_iops,
            )
          
        disk_gb_enabled = ""
        if cluster.get("auto_scaling_disk_gb_enabled") != None:
          disk_gb_enabled = "disk_gb_enabled = {0}".format(cluster.get("auto_scaling_disk_gb_enabled"))
        compute_enabled = ""
        if cluster.get("auto_scaling_compute_enabled") != None:
          compute_enabled = "compute_enabled = {0}".format(cluster.get("auto_scaling_compute_enabled"))
        compute_scale_down_enabled = ""
        if cluster.get("auto_scaling_compute_scale_down_enabled") != None:
          compute_enabled = "compute_scale_down_enabled = {0}".format(cluster.get("auto_scaling_compute_scale_down_enabled"))
        compute_min_instance_size = ""
        if cluster.get("provider_auto_scaling_compute_min_instance_size") != None:
          compute_enabled = "compute_min_instance_size = {0}".format(cluster.get("provider_auto_scaling_compute_min_instance_size"))
        compute_max_instance_size = ""
        if cluster.get("provider_auto_scaling_compute_max_instance_size") != None:
          compute_enabled = "compute_max_instance_size = {0}".format(cluster.get("provider_auto_scaling_compute_max_instance_size"))

        analytics_auto_scaling="""
      analytics_auto_scaling {{
        {disk_gb_enabled}
        {compute_enabled}
        {compute_scale_down_enabled}
        {compute_min_instance_size}
        {compute_max_instance_size}
      }}""".format(
              disk_gb_enabled=disk_gb_enabled,
              compute_enabled=compute_enabled,
              compute_scale_down_enabled=compute_scale_down_enabled,
              compute_min_instance_size=compute_min_instance_size,
              compute_max_instance_size=compute_max_instance_size,
            )
        auto_scaling="""
      auto_scaling {{
        {disk_gb_enabled}
        {compute_enabled}
        {compute_scale_down_enabled}
        {compute_min_instance_size}
        {compute_max_instance_size}
      }}""".format(
              disk_gb_enabled=disk_gb_enabled,
              compute_enabled=compute_enabled,
              compute_scale_down_enabled=compute_scale_down_enabled,
              compute_min_instance_size=compute_min_instance_size,
              compute_max_instance_size=compute_max_instance_size,
            )
        
        backing_provider_name = ""
        if cluster.get("backing_provider_name") != None:
          backing_provider_name = "backing_provider_name = {0}".format(cluster["backing_provider_name"])

        advanced_region_config_tf_config = """
    region_configs {{
      priority = {priority}
      region_name = {region_name}
      provider_name = {provider_name}
      {backing_provider_name}
      {electable_specs}
      {read_only_specs}
      {analytics_specs}
      {analytics_auto_scaling}
      {auto_scaling}
    }}""".format(
          priority=advanced_region_config["priority"], 
          region_name=advanced_region_config["region_name"],
          provider_name=advanced_region_config["provider_name"],
          backing_provider_name=backing_provider_name,
          electable_specs=electable_specs_tf_config,
          read_only_specs=read_only_specs_tf_config,
          analytics_specs=analytics_specs_tf_config,
          analytics_auto_scaling=analytics_auto_scaling,
          auto_scaling=auto_scaling,
        )
        advanced_region_configs.append(advanced_region_config_tf_config)

      replication_spec_tf_config = """
  replication_specs {{
    zone_name = {zone_name}
    num_shards = {num_shards}
    {region_configs}
  }}""".format(
    zone_name=advanced_replication_spec["zone_name"],
    num_shards=advanced_replication_spec["num_shards"],
    region_configs="".join(advanced_region_configs),
  )
      
    advanced_replication_specs.append(replication_spec_tf_config)
  return "".join(advanced_replication_specs)      

# Example usage
filename = "main.tf"
resources = read_terraform_file(filename)

for cluster in clusters:
  # print("Resource found: ", cluster)
  resource_name = cluster.get("resource_name")
  cluster = cluster.get("content")
  advanced_cluster = {}
  advanced_cluster["project_id"] = project_id(cluster)
  advanced_cluster["name"] = name(cluster)
  advanced_cluster["cluster_type"] = cluster_type(cluster)
  advanced_cluster["backup_enabled"] = backup_enabled(cluster)
  advanced_cluster["retain_backups_enabled"] = retain_backups_enabled(cluster)
  advanced_cluster["bi_connector_config"] = bi_connector_config(cluster)
  advanced_cluster["disk_size_gb"] = disk_size_gb(cluster)
  advanced_cluster["encryption_at_rest_provider"] = encryption_at_rest_provider(cluster)
  advanced_cluster["tags"] = tags(cluster)
  advanced_cluster["labels"] = labels(cluster)
  advanced_cluster["mongo_db_major_version"] = mongo_db_major_version(cluster)
  advanced_cluster["pit_enabled"] = pit_enabled(cluster)
  advanced_cluster["termination_protection_enabled"] = termination_protection_enabled(cluster)
  advanced_cluster["version_release_system"] = version_release_system(cluster)
  advanced_cluster["paused"] = paused(cluster)
  advanced_cluster["timeouts"] = timeouts(cluster)
  advanced_cluster["accept_data_risks_and_force_replica_set_reconfig"] = accept_data_risks_and_force_replica_set_reconfig(cluster)
  advanced_cluster["advanced_configuration"] = advanced_configuration(cluster)
  advanced_cluster["replication_specs"] = replication_specs(cluster)


  advanced_cluster_tf_config = """
mongodbatlas_advanced_cluster {resource_name} {{
  {project_id}
  {name}
  {cluster_type}
  {backup_enabled}
  {retain_backups_enabled}
  {bi_connector_config}
  {disk_size_gb}
  {encryption_at_rest_provider}
  {tags}
  {labels}
  {mongo_db_major_version}
  {pit_enabled}
  {termination_protection_enabled}
  {version_release_system}
  {paused}
  {timeouts}
  {accept_data_risks_and_force_replica_set_reconfig}
  {advanced_configuration}
  {replication_specs}
}}""".format(
    resource_name=resource_name, 
    project_id=advanced_cluster['project_id'], 
    name=advanced_cluster['name'], 
    cluster_type=advanced_cluster['cluster_type'],
    backup_enabled=advanced_cluster['backup_enabled'],
    retain_backups_enabled=advanced_cluster['retain_backups_enabled'],
    bi_connector_config=advanced_cluster['bi_connector_config'],
    disk_size_gb=advanced_cluster['disk_size_gb'],
    encryption_at_rest_provider=advanced_cluster['encryption_at_rest_provider'],
    tags=advanced_cluster['tags'],
    labels=advanced_cluster['labels'],
    mongo_db_major_version=advanced_cluster['mongo_db_major_version'],
    pit_enabled=advanced_cluster['pit_enabled'],
    termination_protection_enabled=advanced_cluster['termination_protection_enabled'],
    version_release_system=advanced_cluster['version_release_system'],
    paused=advanced_cluster['paused'],
    timeouts=advanced_cluster['timeouts'],
    accept_data_risks_and_force_replica_set_reconfig=advanced_cluster['accept_data_risks_and_force_replica_set_reconfig'],
    advanced_configuration=advanced_cluster['advanced_configuration'],
    replication_specs=advanced_cluster['replication_specs'],
  )
  temp = advanced_cluster_tf_config
  advanced_cluster_tf_config = []
  for line in temp.split("\n"):
    if line.strip() == "":
      continue
    advanced_cluster_tf_config.append(line)
  print("\n".join(advanced_cluster_tf_config))
