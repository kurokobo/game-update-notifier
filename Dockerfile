FROM python:3.9.2-slim

WORKDIR /app
COPY ./ .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
