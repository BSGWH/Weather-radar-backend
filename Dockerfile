FROM continuumio/miniconda3:latest

# Create the environment
COPY environment.yml /app/environment.yml
WORKDIR /app
RUN conda env create -f environment.yml && \
    conda clean --all --yes

# Activate the environment
SHELL ["conda", "run", "-n", "fastenv", "/bin/bash", "-c"]
ENV PATH=/opt/conda/envs/fastenv/bin:$PATH

# Copy app code

COPY . /app

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"]