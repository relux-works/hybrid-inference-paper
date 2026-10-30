# Paper build. `make pdf` writes dist/hybrid-inference-<version>.ru.pdf and dist/SHA256SUMS.
# The version comes from git tags (.scripts/version.sh); README.md, "Versions and releases".

TECTONIC ?= tectonic
NAME     := hybrid-inference
SHA256   := $(shell command -v sha256sum >/dev/null 2>&1 && echo sha256sum || echo 'shasum -a 256')

.PHONY: pdf clean

pdf:
	@mkdir -p build
	.scripts/version.sh --tex > paper/version.tex
	cd paper && SOURCE_DATE_EPOCH=$$(git log -1 --format=%ct 2>/dev/null || date +%s) \
		$(TECTONIC) -X compile --keep-logs --outdir ../build $(NAME).ru.tex
	rm -rf dist && mkdir dist
	cp build/$(NAME).ru.pdf dist/$(NAME)-$$(.scripts/version.sh).ru.pdf
	cd dist && $(SHA256) *.pdf > SHA256SUMS && cat SHA256SUMS

clean:
	rm -rf build dist paper/version.tex
