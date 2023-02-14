folder:=django_permanent


# Print this help message
help:
	@echo
	@awk '/^#/ {c=substr($$0,3); next} c && /^([a-zA-Z].+):/{ print "  \033[32m" $$1 "\033[0m",c }{c=0}' $(MAKEFILE_LIST) |\
        sort |\
        column -s: -t |\
        less -R

# Sort python files
isort:
	@echo "--- 🐍 Isorting 🐍 ---"
	poetry run isort ${folder}

# Ruffing python files
ruff:
	@echo "--- 🐕 Ruffing 🐕 ---"
	poetry run ruff ${folder}

# Format python files
lint/black:
	@echo "--- 🎩 Blacking 🎩 ---"
	poetry run black ${folder} --check

# Typecheck python files
mypy:
	@echo "--- ⚡ Mypying ⚡ ---"
	poetry run mypy ${folder}

# Run all linters
lint: isort ruff lint/black mypy


# Run all tests
test:
	@echo "--- 💃 Testing 💃 ---"
	poetry run py.test --cov  ${folder}

# Test and lint in CI
ci: lint test



