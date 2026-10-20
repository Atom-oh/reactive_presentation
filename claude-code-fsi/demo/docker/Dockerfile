FROM node:22-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends tmux python3 python3-pip python3-venv jq less locales fonts-noto-cjk \
 && sed -i 's/# ko_KR.UTF-8/ko_KR.UTF-8/; s/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages boto3 requests pytest
RUN npm install -g @anthropic-ai/claude-code && claude --version
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 TERM=xterm-256color
RUN useradd -m -s /bin/bash dev01 && useradd -m -s /bin/bash dev02
WORKDIR /home/dev01
