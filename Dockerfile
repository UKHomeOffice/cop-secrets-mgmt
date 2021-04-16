FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


RUN useradd deploy -d /usr/src/app ; \
    touch /usr/src/app/.netrc ; \
    chown -R deploy /usr/src/app


USER deploy

COPY --chown=1000 aws_secrets ./
COPY --chown=1000 libs ./libs/
COPY --chown=1000 configs ./configs
COPY --chown=1000 projects ./projects
COPY --chown=1000 aws_secrets .
COPY --chown=1000 aws_copy_secrets .

RUN chmod 755 aws_secrets aws_copy_secrets

ENTRYPOINT ["python", "/usr/src/app/aws_secrets"]
