import os
import argparse
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
from github import Github

# read the access token from the environment variable or as a command-line argument
access_token = os.environ.get("ACCESS_TOKEN")
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--token", help="Github access token")
parser.add_argument("-i", "--input", help="Input YAML file")
parser.add_argument("-ik", "--input-key", help="Key to search in the input YAML file", default="sources")
parser.add_argument("-o", "--output", help="Output YAML file")
parser.add_argument("-ok", "--output-key", help="Key to use in the output YAML file", default="kolla-build")
args = parser.parse_args()
if args.token:
    access_token = args.token

# read the input YAML file
input_file = args.input
if not input_file:
    print("No input file specified. Use the -i or --input argument to specify an input YAML file.")
    exit(1)

with open(input_file, "r") as f:
    data = ruamel.yaml.round_trip_load(f, preserve_quotes=True)

# get the default values from the YAML file
default_owner = data[args.input_key]["owner"]
default_branch = data[args.input_key]["branch"]

# get the repository objects
g = Github(access_token)
results = {}
for repository_name, repository_data in data[args.input_key]["repository"].items():
    # get the owner and branch for this repository
    repository_owner = repository_data.get("owner", default_owner)
    repository_branch = repository_data.get("branch", default_branch)

    # get the repository object
    repository = g.get_repo(f"{repository_owner}/{repository_name}")

    # get the branch object for this repository
    branch = repository.get_branch(repository_branch)

    # get the last commit object in the branch
    last_commit = branch.commit

    # get the hash of the last commit
    last_commit_hash = last_commit.sha

    # get the kolla values for this repository
    kolla_values = repository_data.get("kolla")
    if not kolla_values:
        print(f"Error: 'kolla' value missing for repository '{repository_name}'")
        exit(1)
    elif not isinstance(kolla_values, list):
        print(f"Error: 'kolla' value should be a list for repository '{repository_name}'")
        exit(1)

    # add the result to the dictionary
    repository_url = repository.clone_url
    for kolla_value in kolla_values:
        results[kolla_value] = {"location": repository_url, "reference": last_commit_hash, "type": "git"}

# load existing output file if it exists
output_file = args.output
existing_data = {}
if output_file and os.path.exists(output_file):
    with open(output_file, "r") as f:
        existing_data = ruamel.yaml.round_trip_load(f, preserve_quotes=True)

# sort existing keys alphabetically
existing_data = CommentedMap(sorted(existing_data.items()))

# update the output data with the new results
output_data = existing_data.get(args.output_key, CommentedMap())
output_data.update(results)
output_data = CommentedMap(sorted(output_data.items()))
existing_data[args.output_key] = output_data

# sort all keys recursively
def sort_dict_by_key_recursive(d):
    if isinstance(d, dict):
        return CommentedMap((k, sort_dict_by_key_recursive(v)) for k, v in sorted(d.items()))
    elif isinstance(d, list):
        return [sort_dict_by_key_recursive(v) for v in d]
    else:
        return d

existing_data = sort_dict_by_key_recursive(existing_data)

# write the output to the file
if output_file:
    with open(output_file, "w") as f:
        f.write("---\n")
        ruamel.yaml.round_trip_dump(existing_data, f, indent=2, block_seq_indent=2)
        print(f"Successfully generated '{args.output}' file with 'kolla' values for {len(results)} container images.")
else:
    print(ruamel.yaml.round_trip_dump(existing_data, indent=2, block_seq_indent=2))
