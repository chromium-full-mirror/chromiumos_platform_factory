# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM python:3.11-slim

# rsync is for copying files from the factory codebase to the user session workspace
# Ref: py/test_list_editor/middleware/validation.py
RUN apt-get update && apt-get install -y rsync \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 3200 appuser
RUN adduser --disabled-password --gecos '' --uid 3000 --gid 3200 appuser
USER appuser
ENV PATH="$PATH:/home/appuser/.local/bin"
ENV RUNTIME_ENV="prod"

WORKDIR /app

# Copy the requirements first so that changes to python files
# doesn't trigger the package install process again.
COPY --chown=appuser cros/factory/test_list_editor/backend/requirements.txt requirements.txt
RUN pip install pip-tools && \
  pip-sync requirements.txt

COPY --chown=appuser . .

EXPOSE 5000

ENTRYPOINT [ "gunicorn" ]
CMD [ "-b", "0.0.0.0:5000", "cros.factory.test_list_editor.backend.main:app" ]
