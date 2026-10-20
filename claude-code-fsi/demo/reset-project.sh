#!/bin/bash
# Reset the fee-calc project and dev01 Claude Code state inside the container.
docker exec ccfsi bash -c 'mkdir -p /etc/claude-code && cp /opt/scenarios/etc/managed-settings.json /etc/claude-code/ && rm -rf /home/dev01/fee-calc && cp -r /opt/scenarios/fee-calc /home/dev01/ && chown -R dev01:dev01 /home/dev01/fee-calc && rm -rf /home/dev01/batch-job && mkdir -p /home/dev01/batch-job/customer-data && cp /opt/scenarios/fee-calc/customer-data/accounts.csv /home/dev01/batch-job/customer-data/ && chown -R dev01:dev01 /home/dev01/batch-job'
docker exec -u dev01 ccfsi bash -c 'tmux kill-server 2>/dev/null; rm -rf /tmp/tmux-1001 ~/.claude ~/.claude.json
cd ~/fee-calc && git init -q && git add -A && git -c user.name=dev01 -c user.email=dev01@hanasec.example commit -qm "legacy fee module"
echo "{\"hasCompletedOnboarding\":true,\"theme\":\"dark\",\"projects\":{\"/home/dev01/fee-calc\":{\"hasTrustDialogAccepted\":true}}}" > ~/.claude.json
grep -q ANTHROPIC_AUTH_TOKEN ~/.bashrc || echo "export ANTHROPIC_AUTH_TOKEN=tok-dev01-demo  # IdP에서 받은 단기 토큰(데모용 고정값)" >> ~/.bashrc'
echo reset done
