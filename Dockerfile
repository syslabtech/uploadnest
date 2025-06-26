# ---- Node.js Dockerfile for React ----
FROM node:22-alpine as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install -g npm@11.4.2 && npm --version  # Ensure npm 11.4.2 is used
RUN npm ci --omit=dev --prefer-offline --no-audit --progress=false
COPY . .
RUN npm run build

# Serve build with a simple static server
FROM node:22-alpine as production
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build
RUN addgroup -g 10001 appgroup && adduser -D -u 10001 -G appgroup appuser
USER 10001
EXPOSE 80
CMD ["serve", "-s", "build", "-l", "80"]
