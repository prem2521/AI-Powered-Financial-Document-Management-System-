FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Build step if needed, but for dev we use npm start
CMD ["npm", "start"]
