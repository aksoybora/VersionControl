# Version Control Management Tool
This tool provides a version control management system for tracking project dependencies and switching between different versions using Git. It reads version information from version.h files and stores them in a JSON file for reference.

## Features
- Saves the version information of a project and its dependencies.
- Restores projects to a specified version using Git.
- Checks for uncommitted changes before switching versions.

## Installation
### Prerequisites
- Python 3.x
- Git
- gitpython library

### Install Required Packages
`pip install gitpython`

## Usage
Run the script with the following commands:

### Save Version Information
`python script.py save <folder_name>`
- Reads version information from version.h.
- Stores the data in output.json.

### Restore to a Specific Version
`python script.py restore <repo_name> <version>`
- Reads the stored versions from output.json.
- Checks if there are any uncommitted changes in repositories.
- If there are no changes, it switches to the specified version.

### Check Repository Status
`python script.py status`
- Checks if there are any uncommitted changes in repositories.
- Displays the current status.

### JSON File Format
The version data is stored in output.json as follows:
```
{
   "project1": {
       "1.0.0": {
           "dependency1": "1.2.3",
           "dependency2": "2.0.1"
       }
   }
}
```
Example Workflow:
```
# Save the current project version
python script.py save my_project

# Check the status of repositories
python script.py status

# Restore the project to a specific version
python script.py restore my_project 1.0.0
```

## License
This project does not have an open-source license.  
All rights reserved. Unauthorized use, copying, or distribution of this code is prohibited.
