# Mantenha em sincronia com .nvmrc (`make check-pins` confere). O contexto de
# build é frontend/, então o arquivo da raiz não está acessível aqui.
ARG NODE_VERSION=24

FROM node:${NODE_VERSION}-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
