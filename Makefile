# Paper build. `make pdf` writes dist/hybrid-inference-<version>.ru.pdf and dist/SHA256SUMS. The <version> in the file
# name is read back from paper/version.tex, the file the title page prints, so the two always agree.
# The version comes from git tags (.scripts/version.sh); README.md, "Versions and releases".

TECTONIC ?= tectonic
NAME     := hybrid-inference
SHA256   := $(shell command -v sha256sum >/dev/null 2>&1 && echo sha256sum || echo 'shasum -a 256')

.PHONY: pdf clean manifest test-bench

pdf:
	@mkdir -p build
	.scripts/version.sh --tex > paper/version.tex
	cd paper && SOURCE_DATE_EPOCH=$$(git log -1 --format=%ct 2>/dev/null || date +%s) \
		$(TECTONIC) -X compile --keep-logs --outdir ../build $(NAME).ru.tex
	rm -rf dist && mkdir dist
	cp build/$(NAME).ru.pdf dist/$(NAME)-$$(.scripts/version.sh --label-of paper/version.tex).ru.pdf
	cd dist && $(SHA256) *.pdf > SHA256SUMS && cat SHA256SUMS

clean:
	rm -rf build dist paper/version.tex

# MANIFEST.sha256 lists every tracked file except itself; rewrite it after any change.
manifest:
	git ls-files ':!MANIFEST.sha256' | sed 's|^|./|' | xargs $(SHA256) > MANIFEST.sha256

# Tests of the measurement kits' shared helper (bench/*/scripts/kitlib.py).
test-bench:
	python3 -m unittest discover -s bench/tests
