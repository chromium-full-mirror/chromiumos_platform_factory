# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Please build this image at factory codebase root (src/platform/factory).
#
# Build:
#
#     docker build -t hwid_extractor -f py/hwid_extractor/Dockerfile .
#
# Usage:
#
#     docker run --privileged -p 8080:8080 hwid_extractor -p 8080
#
# Then open browser and visit http://localhost:8080.

################################################################################
# Base builder with eseential build tools.

FROM debian:bookworm as base_builder

# Install clang 18 and common build tools.
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends lsb-release software-properties-common gnupg wget make cmake pkg-config git meson ninja-build && \
    mkdir -m 0755 -p /etc/apt/keyrings/ && \
    wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /etc/apt/keyrings/llvm-snapshot.gpg.key && \
    echo "deb [signed-by=/etc/apt/keyrings/llvm-snapshot.gpg.key] http://apt.llvm.org/bookworm/ llvm-toolchain-bookworm-18 main" >> /etc/apt/sources.list && \
    echo "deb-src [signed-by=/etc/apt/keyrings/llvm-snapshot.gpg.key] http://apt.llvm.org/bookworm/ llvm-toolchain-bookworm-18 main" >> /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends clang-18 && \
    update-alternatives --install /usr/bin/cc cc /usr/bin/clang-18 100 && \
    update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++-18 100
ENV CC=/usr/bin/clang-18 CXX=/usr/bin/clang++-18

# TODO(wdzeng): LLVM linker fails to compile flashrom, so use the built-in one.
# Please merge the following RUN command to the above one after solving this
# issue.
#
# RUN apt-get install -y --no-install-recommends lld-18 && \
#     update-alternatives --install /usr/bin/ld ld /usr/bin/ld.lld-18 100
# ENV LD=/usr/bin/ld.lld-18


################################################################################
# Cache servod base image.
#
# TODO(b/344717468): Due to an unknown bug, kaniko on Cloud Run job fails to
# pull servod image at the last stage, so we cache the image here as a
# workaround. We should remove this stage once verify the problem is fixed.

FROM us-docker.pkg.dev/chromeos-hw-tools/servod/servod:release AS servod
WORKDIR /hwid_extractor


################################################################################
# Build libudev.a.

FROM base_builder AS libudev_builder
ARG SYSTEMD_REPO=https://github.com/systemd/systemd.git
ARG SYSTEMD_VERSION=v255

RUN apt-get install -y --no-install-recommends gperf libcap-dev libmount-dev libyaml-dev python3-yaml python3-ply python3-jinja2 liblzma-dev libz-dev gettext && \
    git clone --depth=1 -b ${SYSTEMD_VERSION} ${SYSTEMD_REPO} /systemd && \
    cd /systemd && \
    meson builddir/ -Dstatic-libudev=true && \
    cd builddir && \
    ninja && \
    cp libudev.a /usr/lib/


################################################################################
# Build libpci.a.

FROM base_builder AS libpci_builder
ARG PCIUTILS_REPO=https://github.com/pciutils/pciutils.git
ARG PCIUTILS_VERSION=v3.12.0

RUN git clone --depth=1 -b ${PCIUTILS_VERSION} ${PCIUTILS_REPO} /pciutils && \
    cd /pciutils && \
    make SHARED=no && \
    cp lib/libpci.a /usr/lib


################################################################################
# Build flashrom library.

FROM base_builder AS flashrom_builder
ARG FLASHROM_RPEO=https://chromium.googlesource.com/chromiumos/third_party/flashrom
ARG FLASHROM_VERSION=master

RUN apt-get install -y --no-install-recommends libcmocka-dev libusb-dev libpci-dev && \
    git clone --depth=1 -b ${FLASHROM_VERSION} ${FLASHROM_RPEO} /flashrom && \
    cd /flashrom && \
    meson setup builddir && \
    cd builddir && \
    meson install


################################################################################
# Build flashmap library.

FROM base_builder AS flashmap_builder
ARG FLASHMAP_REPO=https://chromium.googlesource.com/chromiumos/third_party/flashmap
ARG FLASHMAP_VERSION=master

RUN git clone --depth=1 -b ${FLASHMAP_VERSION} ${FLASHMAP_REPO} /flashmap && \
    cd /flashmap && \
    make -j`nproc` && \
    make install


################################################################################
# Build VPD.

FROM base_builder AS vpd_builder
ARG VPD_REPO=https://chromium.googlesource.com/chromiumos/platform/vpd
ARG VPD_VERSION=main
ARG BAZEL_VERSION=7.1.1

# Install bazel.
RUN wget https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel-${BAZEL_VERSION}-linux-x86_64 -qO/usr/bin/bazel && \
    chmod +x /usr/bin/bazel

# Install required libraries.
RUN apt-get install -y --no-install-recommends uuid-dev libz-dev
COPY --from=libudev_builder /usr/lib/libudev.a /usr/lib/
COPY --from=libpci_builder /usr/lib/libpci.a /usr/lib/
COPY --from=flashrom_builder /usr/local/include/libflashrom.h /usr/include/
COPY --from=flashrom_builder /usr/local/lib64/libflashrom.a /usr/lib/
COPY --from=flashmap_builder /usr/include/fmap.h /usr/include/valstr.h /usr/include/
COPY --from=flashmap_builder /usr/lib/libfmap.a /usr/lib/

# Build VPD binary.
ADD py/hwid_extractor/vpd/MODULE.bazel py/hwid_extractor/vpd/MODULE.bazel.lock /workspace/
RUN git clone --depth=1 -b ${VPD_VERSION} ${VPD_REPO} /workspace/vpd
ADD py/hwid_extractor/vpd/BUILD.bazel /workspace/vpd/
RUN cd /workspace && \
    bazel build --action_env=BAZEL_CXXOPTS="-std=c++20" --features=external_include_paths //vpd:vpd && \
    cp ./bazel-bin/vpd/vpd /usr/sbin/vpd


################################################################################
# Build HWID extractor.

FROM servod
COPY --from=vpd_builder /usr/sbin/vpd /usr/sbin/vpd
ADD py/utils/__init__.py \
    py/utils/file_utils.py \
    py/utils/json_utils.py \
    py/utils/platform_utils.py \
    py/utils/process_utils.py \
    py/utils/schema.py \
    py/utils/sync_utils.py \
    py/utils/thread_utils.py \
    py/utils/time_utils.py \
    py/utils/type_utils.py \
    py_pkg/cros/factory/utils/
ADD py/hwid_extractor/*.py py_pkg/cros/factory/hwid_extractor/
ADD py/hwid_extractor/www www

ENV PYTHONPATH="${PYTHONPATH}:/hwid_extractor/py_pkg"
ENV PATH_HWID_EXTRACTOR_WWW="/hwid_extractor/www"
ENV PATH_SERVO_DATA="/usr/local/lib/python3.11/dist-packages/servo/data"
ENTRYPOINT [ "/usr/bin/python3", "/hwid_extractor/py_pkg/cros/factory/hwid_extractor/hwid_extractor.py" ]
CMD [ "-p", "8000" ]
