#!/bin/bash
docker exec -u dev01 ccfsi bash -c 'rm -rf /tmp/tmux-1001; cd ~/fee-calc && tmux new -d -s demo -x 120 -y 40 "bash -i" && tmux set -t demo status off'
bash "$(dirname "$0")/r3-controller.sh" > /dev/null 2>&1 &
sleep 0.5
exec docker exec -it -u dev01 ccfsi tmux attach -t demo
