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
    curr_cluster_stack[-1]["content"][complex_attribute["attr_name"]] = complex_attribute["content"]
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



# Example usage
filename = "main.tf"
resources = read_terraform_file(filename)

for cluster in clusters:
  print("Resource found: ", cluster)
