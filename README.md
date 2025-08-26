# test-codex Development Environment

This repository includes a minimal Docker-based setup for local development.

## Quick start

1. Copy `.env.example` to `.env`:

    ```bash
    cp .env.example .env
    ```
2. Build the images:

    ```bash
    make build
    ```
3. Start the services:

    ```bash
    make up
    ```
4. Run tests (prints the exit code):

    ```bash
    make test
    ```
5. Run linters:

    ```bash
    make lint
    ```
6. Stop and remove containers:

    ```bash
    make down
    ```

The web service is available at <http://localhost:8000>.
