#!/bin/bash

function fail {
	echo "Failed running: $1"
	echo "Exit code: $2"
	exit $2
}

DOCKER_IP=`/sbin/ip route|awk '/default/ { print $3 }'`

gitlab-ctl reconfigure

cd /tmp/backup
tar -xf gitlab_config_*.tar -C /tmp/backup
cp etc/gitlab/gitlab-secrets.json /etc/gitlab/
sed -i "s/# gitlab_rails\['monitoring_whitelist'] = \['127.0.0.0\/8', '::1\/128']/gitlab_rails\['monitoring_whitelist'] = \['$DOCKER_IP']/" /etc/gitlab/gitlab.rb
rm -rf /var/opt/gitlab/backups/*
cp *_gitlab_backup.tar /var/opt/gitlab/backups/ || fail "cp *_gitlab_backup.tar /var/opt/gitlab/backups/" $?
chown git:git /var/opt/gitlab/backups/*_gitlab_backup.tar || fail "chown git:git /var/opt/gitlab/backups/*_gitlab_backup.tar" $?
gitlab-ctl stop puma || fail "gitlab-ctl stop puma" $?
gitlab-ctl stop sidekiq || fail "gitlab-ctl stop sidekiq" $?
GITLAB_ASSUME_YES=1 gitlab-backup restore || fail "gitlab-backup restore" $?

gitlab-ctl reconfigure || fail "gitlab-ctl reconfigure 2." $?
gitlab-ctl restart || fail "gitlab-ctl restart" $?
gitlab-rake gitlab:check SANITIZE=true || fail "gitlab-rake gitlab:check SANITIZE=true" $?
echo "Backup restored successfully"

random_string=$(echo $RANDOM | base64 | head -c 20; echo)

gitlab-rails runner "u = User.new(username: 'backup_test', email: 'test@example.com', name: 'Test User', password: '$random_string$random_string', password_confirmation: '$random_string$random_string'); u.skip_confirmation!; u.save!" || fail "create user" $?
gitlab-rails runner "token = User.find_by_username('backup_test').personal_access_tokens.create(scopes: ['api', 'read_user', 'read_api', 'read_repository', 'write_repository', 'sudo'], name: 'Automation token'); token.set_token('mOD3VhRDOf3qtqvnVQkl'); token.save!" || fail "create access token" $?
echo "Access token created successfully"
