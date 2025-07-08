# Makefile for FalkorDB FastMCP Proxy
# Provides convenient commands for development, testing, and linting

.PHONY: help install install-dev test lint format check clean run docker-build docker-run pre-commit

# Default target
help: ## Show this help message
	@echo "FalkorDB FastMCP Proxy - Development Commands"
	@echo "=============================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install production dependencies
	pip install -r requirements/base.txt

install-dev: ## Install development dependencies
	pip install -r requirements/dev.txt
	pre-commit install

install-prod: ## Install production dependencies with exact versions
	pip install -r requirements/prod.txt

install-ci: ## Install CI/CD dependencies
	pip install -r requirements/ci.txt

# Testing targets
test: ## Run all tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage report
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v

test-integration: ## Run integration tests (requires backend)
	pytest tests/test_remote_mcp.py -v

# Linting and formatting targets
lint: ## Run all linters
	flake8 src/ tests/
	bandit -r src/ --skip B104,B101,B601

lint-full: ## Run all linters including mypy (may have compatibility issues)
	flake8 src/ tests/
	-mypy src/
	bandit -r src/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

format-check: ## Check if code is properly formatted
	black --check src/ tests/
	isort --check-only src/ tests/

# Comprehensive check
check: format-check lint test ## Run all checks (format, lint, test)

# Security check
security: ## Run security checks
	bandit -r src/
	pip-audit

# Cleanup targets
clean: ## Clean up temporary files and caches
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage .pytest_cache/ .mypy_cache/

clean-all: clean ## Clean everything including virtual environments
	rm -rf .venv/ venv/ env/

# Running targets
run: ## Run the unified proxy server
	python src/fastmcp_proxy.py

run-dev: ## Run with development settings
	PROXY_HOST=localhost PROXY_PORT=3001 python src/fastmcp_proxy.py

# Docker targets
docker-build: ## Build Docker image
	docker build -t falkordb-fastmcp-proxy .

docker-run: ## Run Docker container
	docker run -p 3001:3001 -e FALKORDB_MCPSERVER_URL=http://host.docker.internal:3000 falkordb-fastmcp-proxy

docker-compose-up: ## Start with docker-compose
	docker-compose up --build

docker-compose-down: ## Stop docker-compose services
	docker-compose down

# Development tools
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

# Documentation
docs: ## Generate documentation (if docs exist)
	@echo "Documentation generation not yet implemented"

# Version management
version: ## Show current version
	@python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"

# Environment setup
setup-dev: install-dev pre-commit-install ## Complete development environment setup
	@echo "Development environment setup complete!"
	@echo "Run 'make help' to see available commands"

# CI/CD simulation
ci: format-check lint test ## Simulate CI pipeline locally

# Requirements management
compile-deps: ## Generate production lockfile with exact versions
	pip-compile requirements/base.txt --output-file requirements/prod.txt --generate-hashes --no-emit-index-url

update-deps: ## Update all dependencies
	pip-compile --upgrade requirements/base.txt
	pip-compile --upgrade requirements/dev.txt  
	pip-compile --upgrade requirements/base.txt --output-file requirements/prod.txt --generate-hashes --no-emit-index-url

check-deps: ## Check for dependency vulnerabilities  
	pip-audit -r requirements/prod.txt || pip-audit -r requirements/base.txt

sync-deps: ## Sync current environment with requirements
	pip-sync requirements/dev.txt

# Quick development commands
quick-test: ## Run quick tests (exclude slow ones)
	pytest tests/ -v -m "not slow"

watch-test: ## Watch for changes and run tests
	pytest-watch tests/

# Database and backend
check-backend: ## Check if backend is running
	curl -f http://localhost:3000/health || echo "Backend not running on port 3000"

# Token generation for testing
generate-tokens: ## Generate test tokens for development
	python -c "from src.fastmcp_proxy import generate_test_token, generate_tenant_token; print('Bearer Token:', generate_test_token()); print('Tenant Token (acme):', generate_tenant_token('acme', 'admin'))"