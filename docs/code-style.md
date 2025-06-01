# Code Style Guide

## General Guidelines
- Keep the code simple, readable, and maintainable.
- Keep code modular: Break down complex logic into smaller, reusable functions and classes.
- Document your code:
    - Use clear and concise comments to explain complex or non-obvious logic.
    - Write docstrings for all public modules, classes, functions, and methods.
- Aim for a consistent coding style throughout the project.
- Write tests for your code to ensure correctness and prevent regressions.

## Python

### Formatting
- **PEP 8:** Adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/), the official style guide for Python code.
- **Formatter:** We use `autopep8` for automatic PEP 8 formatting. This is configured to run on save within the dev container.
    - Maximum line length: 88 characters is preferred (a common modern standard, though PEP 8 traditionally suggests 79 for code). We have rulers set at 88 and 120 in `.vscode/settings.json` as visual guides.
- **Linters:** `Pylint` is enabled to catch potential errors and style issues. Pay attention to its warnings and suggestions.

### Naming Conventions
- `lowercase_with_underscores` for functions, methods, variables, and modules.
- `UPPERCASE_WITH_UNDERSCORES` for constants.
- `PascalCase` (or `CapWords`) for class names.
- Protected members should be prefixed with a single underscore (e.g., `_internal_var`).
- Private members (name-mangled) should be prefixed with double underscores (e.g., `__private_var`), but use sparingly.

### Imports
- Import modules, not individual functions or classes from them, where it makes sense (e.g., `import requests` then `requests.get()`, not `from requests import get`). This improves clarity.
- Group imports in the following order:
    1. Standard library imports (e.g., `os`, `sys`).
    2. Related third-party imports (e.g., `flask`, `requests`).
    3. Local application/library specific imports.
- Separate each group with a blank line.
- Avoid wildcard imports (`from module import *`).

### Docstrings
- Use [PEP 257](https://www.python.org/dev/peps/pep-0257/) conventions for docstrings.
- For simple, one-line docstrings: `"""This is a concise summary."""`
- For multi-line docstrings:
  ```python
  """Summary line.

  More detailed explanation if needed.

  Args:
      param1 (type): Description of param1.
      param2 (type): Description of param2.

  Returns:
      type: Description of return value.

  Raises:
      SomeError: Why this error might be raised.
  """
  ```

### Type Hinting
- Use [PEP 484](https://www.python.org/dev/peps/pep-0484/) type hints for all function signatures (arguments and return types) and important variables.
- This improves code readability and allows for static analysis.
- Example:
  ```python
  def greet(name: str) -> str:
      return f"Hello, {name}"

  user_name: str = "Alice"
  ```

### Error Handling
- Use specific exception types rather than generic `Exception`.
- Handle exceptions gracefully and provide meaningful error messages.
- Use `try...except...else...finally` blocks appropriately.

## Flask Specifics

### Application Structure
- **Blueprints:** For larger applications, use Blueprints to organize routes and views into modular components. This helps keep the main application file clean.
- **Application Factory Pattern (Optional but Recommended for Growth):** Consider using the application factory pattern (`create_app` function) to initialize your Flask app. This is useful for creating multiple instances of the app (e.g., for testing) and managing configurations.

### Routes and Views
- Keep view functions concise and focused on handling the request and returning a response.
- Business logic should ideally reside in separate modules/services, not directly in view functions.
- Use appropriate HTTP methods (GET, POST, PUT, DELETE, etc.) for your endpoints.
- Return meaningful HTTP status codes.

### Request Handling
- Access request data (e.g., query parameters, JSON body) using Flask's `request` object.
- Validate incoming data. Flask-WTF or libraries like Marshmallow can be helpful for this.

### Configuration
- Manage configuration (e.g., API keys, database URIs) securely. Use environment variables or configuration files (not hardcoded in scripts). Flask's `app.config` object is the standard way to handle this.

### Error Handling
- Use Flask's error handling mechanisms (`@app.errorhandler`) to define custom error pages or JSON responses for specific HTTP error codes.

## Library-Specific Guidelines

### `requests` (for Scryfall API)
- **Error Handling:** Always check the `status_code` of the response. Raise exceptions or handle errors for non-2xx status codes.
- **Timeouts:** Set explicit timeouts for requests to prevent indefinite blocking (e.g., `requests.get(url, timeout=5)`).
- **Session Objects:** If making multiple requests to the same host (Scryfall), use a `requests.Session` object. It can provide performance benefits (e.g., connection pooling) and persist certain parameters (like headers) across requests.
- **User-Agent:** It's good practice to set a custom `User-Agent` header to identify your application when making API requests.

### `spaCy` / `NLTK` (for NLP)
- **Model Management:** Clearly document which NLP models are used and how to download/load them.
- **Processing Pipelines:** If using spaCy, be mindful of the components in your processing pipeline (`nlp.pipe_names`). Disable unnecessary components for performance if you only need specific features (e.g., just tokenization and POS tagging).
- **Efficiency:** Process texts in batches if possible, rather than one by one, for better performance.
- **Clarity:** Keep NLP processing logic separate and well-documented, as it can become complex.

### `NetworkX` (for Synergy Graphs)
- **Node/Edge Definitions:** Clearly define what constitutes a node (e.g., a card) and an edge (e.g., a synergy type) in your graph.
- **Attributes:** Store relevant information as attributes on nodes and edges (e.g., card properties, synergy strength).
- **Graph Size:** Be mindful of the potential size of the graph. For very large graphs, consider performance implications of different algorithms.
- **Visualization (Optional):** If visualizing graphs, ensure the visualizations are clear and serve a purpose.

## General Best Practices
- **DRY (Don't Repeat Yourself):** Avoid duplicating code. Use functions, classes, and modules to promote reusability.
- **KISS (Keep It Simple, Stupid):** Prefer simple solutions over complex ones, unless the complexity is justified.
- **YAGNI (You Ain't Gonna Need It):** Don't implement features that are not currently required.
- **Code Reviews:** If working in a team, conduct code reviews to improve code quality and share knowledge.
