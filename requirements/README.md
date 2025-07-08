# Requirements Management

This directory contains the dependency management files for different environments and use cases.

## File Structure

```
requirements/
├── base.txt      # Core production dependencies (minimal)
├── dev.txt       # Development tools and testing dependencies  
├── prod.txt      # Production with exact versions and hashes
├── ci.txt        # CI/CD pipeline tools
└── README.md     # This file
```

## Standard Practice Explanation

### 1. **base.txt** - Production Core
- **Purpose**: Minimal dependencies needed to run the application
- **Version Strategy**: Use ranges (`>=x.y.z,<major+1.0.0`) for flexibility
- **Who Uses**: Docker images, production deployments, end users
- **Example**: `fastapi>=0.104.0,<1.0.0`

### 2. **dev.txt** - Development Environment  
- **Purpose**: Everything developers need locally (includes base.txt)
- **Contents**: Testing tools, linters, formatters, type checkers
- **Who Uses**: Local development, pre-commit hooks
- **Example**: Includes pytest, flake8, black, mypy

### 3. **prod.txt** - Production Lockfile
- **Purpose**: Exact versions with cryptographic hashes for security
- **Generation**: `pip-compile base.txt --output-file prod.txt --generate-hashes`
- **Who Uses**: Production deployments, security-conscious environments
- **Example**: `fastapi==0.104.1 --hash=sha256:abc123...`

### 4. **ci.txt** - CI/CD Pipeline
- **Purpose**: Tools needed for automated testing and deployment
- **Contents**: Coverage tools, parallel testing, packaging tools
- **Who Uses**: GitHub Actions, Jenkins, other CI systems
- **Example**: Includes tox, coverage, build tools

## Usage Examples

### Local Development
```bash
# Full development environment
pip install -r requirements/dev.txt

# Or use the convenience Makefile
make install-dev
```

### Production Deployment
```bash
# For maximum security (recommended)
pip install -r requirements/prod.txt

# For flexibility (not recommended in production)
pip install -r requirements/base.txt
```

### CI/CD Pipeline
```bash
# In GitHub Actions or similar
pip install -r requirements/ci.txt
```

### Docker Builds
```dockerfile
# Production Docker image
COPY requirements/base.txt requirements/
RUN pip install -r requirements/base.txt

# Development Docker image  
COPY requirements/dev.txt requirements/
RUN pip install -r requirements/dev.txt
```

## Maintenance Workflow

### 1. Adding New Dependencies

1. **Add to appropriate base file**: Edit `base.txt` for production deps, `dev.txt` for dev tools
2. **Update lockfile**: Run `pip-compile` to regenerate `prod.txt`
3. **Test thoroughly**: Ensure compatibility across environments
4. **Commit all files**: Include both source and generated files

### 2. Updating Dependencies

```bash
# Update base dependencies
pip-compile --upgrade requirements/base.txt

# Update dev dependencies  
pip-compile --upgrade requirements/dev.txt

# Update production lockfile with hashes
pip-compile --upgrade requirements/base.txt \
  --output-file requirements/prod.txt \
  --generate-hashes \
  --no-emit-index-url
```

### 3. Security Updates

```bash
# Scan for vulnerabilities
pip-audit -r requirements/prod.txt

# Update only security fixes
pip-compile --upgrade-package vulnerable-package>=fixed.version requirements/base.txt
```

## Best Practices

### ✅ DO
- Use version ranges in base files for flexibility
- Generate exact versions with hashes for production
- Separate development and production dependencies
- Include transitive dependencies explicitly in prod.txt
- Regular security scanning with pip-audit
- Document breaking changes in version updates

### ❌ DON'T  
- Use exact versions (==) in base.txt (reduces flexibility)
- Include development tools in production deployments
- Skip the lockfile generation for production
- Commit without testing dependency changes
- Use `pip freeze > requirements.txt` (includes everything)

## pyproject.toml vs requirements.txt

This project uses **both** approaches:

- **pyproject.toml**: Modern Python packaging standard, metadata, tool config
- **requirements.txt**: Traditional, better CI/CD tooling support, Docker-friendly

The `pyproject.toml` defines the same dependencies in the `[project]` section for packaging, while requirements files provide the granular control needed for different deployment scenarios.

## Tools Integration

- **pip-tools**: For generating lockfiles (`pip-compile`)
- **Dependabot**: Automated dependency updates (GitHub)
- **pip-audit**: Security vulnerability scanning  
- **safety**: Alternative security scanner
- **renovate**: Advanced dependency management (alternative to Dependabot)

This structure follows Python packaging best practices and provides maximum flexibility for different deployment scenarios while maintaining security and reproducibility.