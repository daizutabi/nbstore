FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu24.04

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-luatex \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-lang-japanese \
    libcairo2 \
    poppler-utils \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/*