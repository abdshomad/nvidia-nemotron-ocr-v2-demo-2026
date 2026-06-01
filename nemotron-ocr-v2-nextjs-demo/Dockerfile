FROM node:20-alpine
WORKDIR /app

# Copy package lockfiles first for caching
COPY package*.json ./
RUN npm ci

# Copy nextjs application source files
COPY . .

# Build production app
ENV NODE_ENV=production
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
