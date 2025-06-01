## Commit Style Guide

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) style for our commit messages. Additionally, every commit message must include:

1. A list of files changed.
2. A brief explanation of the reasons for the changes.

### Examples:
- `feat: add new user authentication module`
  - **Files Changed**: `auth.js`, `userController.js`
  - **Reason**: Added a new authentication module to support OAuth.

- `fix: resolve issue with data fetching.`
  - **Files Changed**: `dataService.js`
  - **Reason**: Fixed a bug causing incorrect API responses.

- `docs: update README with installation instructions`
  - **Files Changed**: `README.md`
  - **Reason**: Added detailed installation steps for new developers.

- `style: format code with Prettier`
  - **Files Changed**: Various
  - **Reason**: Consistent code formatting.

- `refactor: improve performance of data processing`
  - **Files Changed**: `dataProcessor.js`
  - **Reason**: Optimized algorithms for better performance.

- `test: add unit tests for user service`
  - **Files Changed**: `userService.test.js`
  - **Reason**: Increased test coverage for the user service.

- `chore: update dependencies`
  - **Files Changed**: `package.json`, `package-lock.json`
  - **Reason**: Updated dependencies to their latest versions.
