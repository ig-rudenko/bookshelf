FROM node:24.2.0-alpine AS builder

WORKDIR /app

# this will allow us to run vite and other tools directly
ENV PATH=/usr/src/node_modules/.bin:$PATH

COPY package.json .

RUN npm install;

COPY . .

RUN npm run build


FROM nginx:1.28.0-alpine AS prod

COPY --from=builder /app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
