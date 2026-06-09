# ---- Build Stage ----
FROM node:20-alpine AS build

WORKDIR /app

# 先复制依赖文件，利用缓存层
COPY package.json package-lock.json* ./
RUN npm ci

# 复制源码并构建
COPY . .
RUN npm run build

# ---- Production Stage ----
FROM nginx:1.26-alpine

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:80/ > /dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
