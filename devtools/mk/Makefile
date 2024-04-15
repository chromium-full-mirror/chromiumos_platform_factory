# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
REQUIREMENTS_INPUTS = \
	coverage.requirements.in \
	mypy.requirements.in \
	pylint.requirements.in \
	sphinx.requirements.in \
	yapf.requirements.in
REQUIREMENTS_OUTPUTS = $(REQUIREMENTS_INPUTS:.in=.txt)

.PHONY: help clean requirements

help:
	@echo "Use \`make <target>' where <target> is one of"
	@echo "  requirements to update requirements.txt from requirements.in"
	@echo "  clean        to remove all built targets"

clean:
	rm -f $(REQUIREMENTS_OUTPUTS)

requirements: $(REQUIREMENTS_OUTPUTS)

$(REQUIREMENTS_OUTPUTS): %.txt: %.in ./create_requirements_with_hash.sh
	./create_requirements_with_hash.sh $<
