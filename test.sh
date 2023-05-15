#!/bin/bash

GITLAB_HOME=/Users/gitlab # set this to your GitLab home directory

if [ -z "$GITLAB_HOME" ]; then
  echo "Please set GITLAB_HOME to your GitLab home directory"
  exit 1
fi

trap "{ echo 'Destroying GitLab instance...'; sudo docker rm -f gitlab; exit 1; }" SIGINT SIGTERM EXIT

BACKUP=`ls $GITLAB_HOME/backup | grep gitlab_backup`
IFS='_' read -ra BACKUP_ARRAY <<< "$BACKUP"
GITLAB_VERSION=${BACKUP_ARRAY[4]}

echo "GitLab version: $GITLAB_VERSION"

sudo docker run --detach \
  --publish 443:443 --publish 80:80 --publish 22:22 \
  --name gitlab \
  --restart always \
  --volume $GITLAB_HOME/config:/etc/gitlab \
  --volume $GITLAB_HOME/logs:/var/log/gitlab \
  --volume $GITLAB_HOME/data:/var/opt/gitlab \
  --volume $GITLAB_HOME/backup:/tmp/backup \
  --shm-size 256m \
  gitlab/gitlab-ce:$GITLAB_VERSION-ce.0

cp *.tar $GITLAB_HOME/backup
cp restore_backup.sh $GITLAB_HOME/backup

sudo docker exec -it gitlab /bin/bash -c "cd /tmp/backup && chmod +x restore_backup.sh && ./restore_backup.sh"
if [ $? -ne 0 ]; then
  echo "Backup failed"
  exit 1
fi

echo "Backup restored successfully"
python3 run_checks.py
