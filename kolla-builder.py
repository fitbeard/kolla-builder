import argparse
import configparser
import os
from github import Github
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

# Set up the argument parser
parser = argparse.ArgumentParser(description="kolla-builder")
subparsers = parser.add_subparsers(dest='command', help='Commands')

access_token = os.environ.get("ACCESS_TOKEN")

# update-sources sub-command
update_sources_parser = subparsers.add_parser('update-sources', help='Update sources for kolla-build')
update_sources_parser.add_argument("-t", "--token", help="Github access token")
update_sources_parser.add_argument("-i", "--input", required=True, help="Input YAML file")
update_sources_parser.add_argument("-ik", "--input-key", help="Key to search in the input YAML file", default="sources")
update_sources_parser.add_argument("-o", "--output", help="Output YAML file")
update_sources_parser.add_argument("-ok", "--output-key", help="Key to use in the output YAML file", default="kolla-build")

# generate-config sub-command
generate_config_parser = subparsers.add_parser('generate-config', help='Generate kolla-build.conf')
generate_config_parser.add_argument("-i", "--input", required=True, help="Input YAML file")
generate_config_parser.add_argument("-ik", "--input-key", help="Key to search in the input YAML file", default="kolla-build")
generate_config_parser.add_argument("-o", "--output", required=True, help="Output INI file")

args = parser.parse_args()

def update_sources():
    token = args.token if args.token else access_token
    if not token:
        print("Error: GitHub access token must be provided via --token or ACCESS_TOKEN environment variable.")
        exit(1)

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent = 2
    yaml.block_seq_indent = 2

    with open(args.input, "r") as f:
        data = yaml.load(f)

    default_owner = data[args.input_key].get("owner")
    default_branch = data[args.input_key].get("branch")

    if not default_owner or not default_branch:
        print("Error: 'owner' and 'branch' must be provided in the input YAML file.")
        exit(1)

    g = Github(token)
    results = {}
    for repository_name, repository_data in data[args.input_key]["repository"].items():
        repository_owner = repository_data.get("owner", default_owner)
        repository_branch = repository_data.get("branch", default_branch)

        try:
            repository = g.get_repo(f"{repository_owner}/{repository_name}")
            branch = repository.get_branch(repository_branch)
            last_commit = branch.commit
            last_commit_hash = last_commit.sha
        except Exception as e:
            print(f"Error: Unable to access repository '{repository_owner}/{repository_name}' or branch '{repository_branch}': {e}")
            continue

        kolla_values = repository_data.get("kolla")
        if not kolla_values or not isinstance(kolla_values, list):
            print(f"Error: 'kolla' value should be a list for repository '{repository_name}'")
            exit(1)

        repository_url = repository.clone_url
        for kolla_value in kolla_values:
            results[kolla_value] = {"location": repository_url, "reference": last_commit_hash, "type": "git"}

    output_file = args.output
    existing_data = CommentedMap()
    if output_file and os.path.exists(output_file):
        with open(output_file, "r") as f:
            loaded_data = yaml.load(f)
            if loaded_data:
                existing_data = CommentedMap(loaded_data)

    existing_data = CommentedMap(sorted(existing_data.items()))
    output_data = existing_data.get(args.output_key, CommentedMap())
    output_data.update(results)
    output_data = CommentedMap(sorted(output_data.items()))
    existing_data[args.output_key] = output_data

    def sort_dict_by_key_recursive(d):
        if isinstance(d, dict):
            return CommentedMap((k, sort_dict_by_key_recursive(v)) for k, v in sorted(d.items()))
        elif isinstance(d, list):
            return [sort_dict_by_key_recursive(v) for v in d]
        else:
            return d

    existing_data = sort_dict_by_key_recursive(existing_data)

    if output_file:
        with open(output_file, "w") as f:
            f.write("---\n")
            yaml.dump(existing_data, f)
            print(f"Successfully generated '{output_file}' file with 'kolla' values for {len(results)} container images.")
    else:
        print(yaml.dump(existing_data))

def generate_config():
    yaml = YAML()

    with open(args.input, "r") as f:
        data = yaml.load(f)

    input_key = args.input_key if args.input_key else "kolla-build"
    config = configparser.ConfigParser()

    if 'DEFAULT' in data[input_key]:
        for key, value in data[input_key]['DEFAULT'].items():
            config.defaults()[key] = str(value)

    for section in data[input_key]:
        if section == 'DEFAULT':
            continue
        config.add_section(section)
        for key, value in data[input_key][section].items():
            config.set(section, key, str(value))

    with open(args.output, 'w') as f:
        config.write(f)

    print(f'Successfully converted {args.input}:{input_key} to {args.output}')

if args.command == 'update-sources':
    update_sources()
elif args.command == 'generate-config':
    generate_config()
else:
    parser.print_help()
    exit(1)
