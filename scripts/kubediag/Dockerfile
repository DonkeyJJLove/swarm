# Bazowy obraz
FROM debian:bullseye-slim

# Metadane
LABEL maintainer="twoj.email@domena.com"
LABEL description="KubeDiag Toolkit - Obraz diagnostyczny z narzędziami pentesterskimi dla Kubernetes"

# Instalacja niezbędnych narzędzi
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nmap \
    dnsutils \
    net-tools \
    tcpdump \
    telnet \
    iproute2 \
    vim \
    less \
    iperf3 \
    nikto \
    traceroute \
    htop \
    metasploit-framework \
    && rm -rf /var/lib/apt/lists/*

# Instalacja kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Instalacja Python i zależności
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Kopiowanie skryptów
COPY diagnostic_logic.py /app/diagnostic_logic.py

# Ustawienie katalogu roboczego
WORKDIR /app

# Ustawienie domyślnego użytkownika
USER root

# Ustawienie domyślnego terminala
CMD ["/bin/bash"]
