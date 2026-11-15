FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=http://localhost:8000
ARG VITE_USAR_MOCK=false
ARG VITE_SONIDO_ALERTAS=true

ENV VITE_API_URL=$VITE_API_URL \
    VITE_USAR_MOCK=$VITE_USAR_MOCK \
    VITE_SONIDO_ALERTAS=$VITE_SONIDO_ALERTAS

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
