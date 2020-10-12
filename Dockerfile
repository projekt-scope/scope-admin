FROM continuumio/miniconda3:4.7.12-alpine
#############
# As `root` #
#############
USER root

ENV PATH=/opt/conda/bin:$PATH
# install git
RUN apk add --update git openssh gnupg vim shadow


COPY requirements.txt .
RUN conda create --name my && \
    . activate my && \
    pip install -r requirements.txt

ENV PATH=/opt/conda/envs/my/bin:$PATH

RUN apk add --no-cache \
    dumb-init

ENV HOME=/home/anaconda
RUN ln -s ${HOME}/app /app

#################
# As `root` #
#################
USER root
WORKDIR /app

# Activate the conda environment `my` for login and non-login shells. See the
# section "Invocation" of https://linux.die.net/man/1/ash
RUN echo ". activate my" >> ~/.shinit
ENV ENV=${HOME}/.shinit

COPY --chown=anaconda:anaconda . .
EXPOSE 1234

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
# CMD ["python3", "runserver.py", "--port", "1234"]
