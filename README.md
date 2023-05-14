# GitLab Backup Verify
Simple script for validating GitLab backups.

## Pre-requisites
* Docker
* Python 3.6+
* pip3

## How it works
The script will start a GitLab instance using the `gitlab/gitlab-ce` Docker image. It will then restore the backup and run a series of tests to verify the backup is valid. The tests are simple and small. They check if:
* the GitLab instance is working
* the number of users and projects is correct
* it is possible to create a new project

## How to use
1. Install the Python dependencies: `pip3 install -r requirements.txt`.
2. Set the `$GITLAB_HOME` variable in `test.sh` (or set environmental variable) to the path which Docker will mount the GitLab data directory to.
3. Set `config.yaml` to match your GitLab configuration.
4. Place your GitLab backup (config backup is also required) in the root directory of this repostitory. They will be copied to `$GITLAB_HOME/backups` when the script is run.
5. Run the script: `./test.sh`.
