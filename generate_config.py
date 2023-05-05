import argparse
import os
import yaml
import configparser

# Set up the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input YAML file")
parser.add_argument("-ik", "--input-key", help="Key to search in the input YAML file", default="kolla-build")
parser.add_argument("-o", "--output", help="Output YAML file")
args = parser.parse_args()

# Check if input and output file paths were provided as command-line arguments
if args.input and args.output:
    input = args.input
    output = args.output

# If not, print an error message and exit
else:
    print('Error: input and output file paths must be provided as command-line arguments')
    exit(1)

# Load the YAML file into a dictionary
with open(input) as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

# Check if the output source was provided as a command-line argument
if args.input_key:
    input_key = args.input_key

# Create a ConfigParser object to store the INI data
config = configparser.ConfigParser()

# Check if the output source has a 'DEFAULT' section and add it to the ConfigParser defaults
if 'DEFAULT' in data[input_key]:
    for key, value in data[input_key]['DEFAULT'].items():
        config.defaults()[key] = str(value)

# Loop through each section of the selected dictionary and add it to the ConfigParser
for section in data[input_key]:
    if section == 'DEFAULT':
        continue
    config.add_section(section)
    for key, value in data[input_key][section].items():
        config.set(section, key, str(value))

# Write the ConfigParser data to the output file
with open(output, 'w') as f:
    config.write(f)

print(f'Successfully converted {input}:{input_key} to {output}')
