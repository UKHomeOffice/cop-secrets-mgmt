FROM python:3
ENV DRONE_VERSION ${DRONE_VERSION}

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd secrets

USER secrets

COPY --chown=1000 *.py ./
RUN chmod 755 *.py

ENTRYPOINT ["python", "/usr/src/app/aws_secrets.py"]
