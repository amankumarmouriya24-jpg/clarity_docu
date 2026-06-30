# Contributing to ClarityDoc

Thank you for your interest in contributing to ClarityDoc! This document outlines the process for contributing to the project.

## Getting Started

1. Fork or clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r backend/requirements.txt`
5. Copy `.env.example` to `.env` and add your API keys

## Development Workflow

1. Create a new branch for your feature or fix:
   ```
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run the test suite locally before committing:
   ```
   python -m unittest discover -s tests
   ```
4. Commit using [Conventional Commits](https://www.conventionalcommits.org/) format (see below)
5. Push your branch and open a merge request

## Commit Message Format (Semantic Commits)

We follow the Conventional Commits specification:

```
<type>(<scope>): <short summary>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes only
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `chore`: Build process, dependency updates, tooling changes
- `ci`: Changes to CI/CD configuration

**Examples:**
```
feat(api): add document summarization endpoint
fix(auth): resolve token expiration bug
docs(readme): update installation instructions
ci(pipeline): add security scan stage
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all public functions
- Keep functions focused and under 50 lines where possible

## Pre-commit Checks

Before committing, ensure:
- [ ] Code is formatted (`black .`)
- [ ] Linting passes (`flake8 .`)
- [ ] Type checks pass (`mypy .`)
- [ ] Security scan is clean (`bandit -r .`)
- [ ] All tests pass
- [ ] Commit message follows semantic format

## Reporting Issues

When reporting a bug, please include:
- A clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

## Pull Request / Merge Request Process

1. Ensure all CI/CD pipeline checks pass
2. Update documentation if needed
3. Request review from a maintainer
4. Address any review feedback
5. Once approved, your changes will be merged

## Code of Conduct

Be respectful, constructive, and collaborative. We're building this together.
