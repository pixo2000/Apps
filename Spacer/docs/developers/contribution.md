# Contributing to Spacer

Thank you for your interest in contributing to Spacer! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository and clone it locally
2. Set up your development environment
3. Familiarize yourself with the code structure (see [File Structure](file_structure.md))
4. Check the existing issues or create a new one describing what you plan to work on

## Development Environment

Spacer is built with Python and requires minimal dependencies:
- Python 3.6 or higher
- `tqdm` library (optional, for progress bars)
- `pytz` library (optional, for timezone handling)

## Coding Standards

Please follow these coding standards when contributing:

1. **Code Style**: Follow PEP 8 style guidelines
2. **Documentation**: Add docstrings to new functions and classes
3. **Comments**: Include comments for complex logic
4. **Imports**: Organize imports alphabetically and group by standard library, third-party, and local
5. **Error Handling**: Use try/except blocks for operations that might fail

## Pull Request Process

1. Create a new branch for your feature or bugfix
2. Make your changes, adhering to the coding standards
3. Test your changes thoroughly
4. Update documentation if necessary
5. Submit a pull request with a clear description of your changes

## Feature Development Guidelines

When adding new features:

### New Commands

If adding a new command:
1. Add the command handler in `player_input.py`
2. Follow the existing pattern for command parsing
3. Update the help documentation

### New Dimensions

If adding new dimensions:
1. Follow the structure in [Adding Dimensions](adding_dimensions.md)
2. Test thoroughly with scanning and navigation

### Game Mechanics

If modifying core game mechanics:
1. Ensure backward compatibility with existing save files
2. Update relevant documentation
3. Consider the impact on player experience

## Bug Fixes

When fixing bugs:

1. Clearly reference the issue being fixed
2. Include test steps to verify the fix
3. Consider adding error handling to prevent similar issues

## Documentation

Update documentation when:

1. Adding new commands
2. Changing game mechanics
3. Modifying save file structure
4. Adding new dimension features

## Testing

Before submitting changes:

1. Test starting a new game
2. Test loading existing save files
3. Test all affected commands
4. Verify save/load functionality still works

## Code Review Process

All submissions will be reviewed for:

1. Code quality
2. Adherence to style guidelines
3. Proper error handling
4. Documentation completeness
5. Game balance and player experience

## Contact

If you have questions about contributing, please create an issue in the repository with your question.

Thank you for helping improve Spacer!
