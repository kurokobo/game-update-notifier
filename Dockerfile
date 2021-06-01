FROM python:3.9.2-slim

RUN groupadd -r bot && \
    useradd -r -m -d /app -g bot bot && \
    mkdir -p /app/.config /app/cache && \
    chown -R bot:bot /app
USER bot

WORKDIR /app

COPY ./requirements.txt .
RUN python -m pip install --upgrade pip --no-warn-script-location && \
    python -m pip install -r requirements.txt --no-warn-script-location

COPY ./ .

VOLUME ["/app/.config", "/app/cache"]

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
