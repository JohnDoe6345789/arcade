FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_MAJOR=20 \
    PATH="/usr/local/bin:${PATH}"

# Base tools and Node 20.x from NodeSource
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates gnupg && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip \
      nodejs \
      pngcheck imagemagick libxml2-utils inkscape \
      libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
      fonts-dejavu-core git jq && \
    npm install -g svgo svglint && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir cairosvg pytest && \
    rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/nodesource.list

WORKDIR /workspace

CMD ["bash"]
