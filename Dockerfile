FROM python:3.8-alpine

RUN apk add ipmitool

COPY ./src/ ./src/
