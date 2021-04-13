# Payments service

### SQL Alchemy migrations

- Init (first time only)
  - **flask db init**
- Create migration (after each model change)
  - **flask db migrate**
- Apply migration (after migration created)
  - **flask db upgrade**

### Docker build and run
- Build
    - **docker build -t payments:0.0.1 .**
- Run
    - **docker-compose up -d**
- Runs on port **5005**