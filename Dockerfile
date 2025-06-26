# ---- Frontend Dockerfile ----
FROM node:22-alpine as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install -g npm@11.4.2 && npm --version  # Ensure npm 11.4.2 is used
RUN npm ci --omit=dev --prefer-offline --no-audit --progress=false
COPY . .
RUN npm run build

# Serve with minimal image
FROM nginx:alpine as production
LABEL maintainer="Your Name <your@email.com>"
WORKDIR /usr/share/nginx/html
RUN addgroup -g 10001 appgroup && adduser -D -u 10001 -G appgroup appuser
COPY --from=build /app/build .
COPY nginx.conf /etc/nginx/nginx.conf
RUN touch .env && chmod 600 .env && chown appuser:appgroup .env
USER 10001
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
