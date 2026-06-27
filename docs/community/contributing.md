# Contributing

Thank you for your interest in contributing to django-custom-storage! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to the Python Software Foundation's Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/django-custom-storage.git
   cd django-custom-storage
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[testing,linting]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run the test suite:

```bash
python runtests.py
```

Run tests for specific Django/Python versions using tox:

```bash
tox
```

Run tests for a specific environment:

```bash
tox -e py310-django52
```

### Code Quality

Before submitting code, ensure:

1. All tests pass: `python runtests.py`
2. Code passes linting: `flake8 src tests`
3. Code is formatted: `black src tests`
4. Imports are sorted: `isort src tests`
5. Type checking passes (if applicable): `mypy src`

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking (optional)

## Making Changes

### Development Workflow

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write/update tests

3. Ensure all tests pass and code quality checks pass

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request on GitHub

### Commit Messages

Follow these guidelines for commit messages:

- Use clear, descriptive commit messages
- Start with a capital letter
- Use imperative mood ("Add feature" not "Added feature")
- Keep the first line under 72 characters
- Add more detailed explanation if needed in the body

Example:
```
Add support for Django 5.2

- Update get_storage_class to use import_string for Django 5.2+
- Add tests for Django 5.2 compatibility
- Update tox.ini to include Django 5.2 test environments
```

### Pull Request Guidelines

When creating a Pull Request:

1. **Describe your changes**: Provide a clear description of what your PR does
2. **Reference issues**: If your PR fixes an issue, reference it (e.g., "Fixes #123")
3. **Add tests**: Include tests for new features or bug fixes
4. **Update documentation**: Update relevant documentation if needed
5. **Keep PRs focused**: One PR should address one issue or feature
6. **Ensure CI passes**: All CI checks must pass before merge

### Testing Guidelines

- Write tests for all new features
- Write tests for bug fixes
- Ensure tests cover edge cases
- Aim for high test coverage (maintain or improve coverage)
- Follow existing test patterns and structure

Test files should be in the `tests/` directory and follow the naming convention `test_*.py`.

### Documentation Guidelines

- Update README.md if needed
- Update documentation in `docs/` directory
- Add docstrings to new functions and classes
- Follow existing documentation style

### Code Style

Follow PEP 8 style guidelines with these specific rules:

- Maximum line length: 80 characters (enforced by flake8)
- Use 4 spaces for indentation
- Use type hints where appropriate
- Follow Django coding style for Django-specific code

The project uses Black for automatic code formatting, so run `black` before committing.

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Step-by-step instructions
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: Python version, Django version, OS
6. **Error messages**: Full error traceback if applicable
7. **Code samples**: Minimal code sample that reproduces the issue

Create a bug report in the [Issues](https://github.com/DLRSP/django-custom-storage/issues) section.

## Suggesting Features

Feature suggestions are welcome! When suggesting features:

1. **Describe the feature**: Clear description of what you want
2. **Explain the use case**: Why this feature would be useful
3. **Provide examples**: Code examples of how it would be used
4. **Consider alternatives**: Any alternative approaches you've considered

Create a feature request in the [Issues](https://github.com/DLRSP/django-custom-storage/issues) section.

## Release Process

Releases are managed by maintainers. The version is managed using bumpversion:

- Patch release: `exec_bump-patch.bat`
- Minor release: `exec_bump-minor.bat`
- Major release: `exec_bump-major.bat`

## Questions?

If you have questions about contributing:

- Check existing [Issues](https://github.com/DLRSP/django-custom-storage/issues)
- Check existing [Pull Requests](https://github.com/DLRSP/django-custom-storage/pulls)
- Create a new issue with the "question" label

## License

By contributing to django-custom-storage, you agree that your contributions will be licensed under the MIT License.
