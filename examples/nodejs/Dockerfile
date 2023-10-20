# syntax=docker/dockerfile:1.3-labs
FROM node

WORKDIR /app/

COPY package.json package-lock.json /app/

RUN npm install

COPY server.js /app/

CMD node server.js
