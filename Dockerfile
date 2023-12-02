FROM python:3.10-alpine

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 443
EXPOSE 80
EXPOSE 88
EXPOSE 8443
CMD ["python3", "main.py"]