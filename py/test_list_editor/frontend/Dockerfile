# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM node:18-alpine AS builder
ENV NODE_ENV=production

WORKDIR /app

COPY . /app

RUN npm ci && npm run build

FROM nginx:1.25.3-alpine-slim AS server

COPY --from=builder /app/build/ /usr/share/nginx/http

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 6000

CMD ["nginx", "-g", "daemon off;"]
