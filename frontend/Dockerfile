FROM node:20.15-alpine3.20 as builder

WORKDIR /app

# this will allow us to run vite and other tools directly
ENV PATH /usr/src/node_modules/.bin:$PATH

COPY package.json .

RUN npm install;

COPY . .

RUN npm run build


FROM nginx:1.25.4-alpine as prod

COPY --from=builder /app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
