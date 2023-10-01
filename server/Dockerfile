ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim
WORKDIR /server
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000
WORKDIR /
ENTRYPOINT [ "/entrypoint.sh" ]
