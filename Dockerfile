FROM python:3-alpine

WORKDIR /bavi
COPY requirements.txt ./

RUN apk add --update --no-cache g++ gcc libxslt-dev gettext
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD /bin/sh -c "envsubst < /bavi/docker.conf.tmpl > /bavi/docker.conf && python bavi.py -c /bavi/docker.conf"
