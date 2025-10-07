FROM node:20-slim

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

ARG VITE_API_BASE=http://localhost:8080
ENV VITE_API_BASE=$VITE_API_BASE

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
