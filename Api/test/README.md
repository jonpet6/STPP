# Testing

## [Setup](./setup)
1. Create venv with [dependencies](./setup/dependencies.py)
2. Create [resources](./resources)
    1. Generate rsa keys ([public.pem](./resources/public.pem), [private.key](./resources/private.key))
        * https://travistidwell.com/jsencrypt/demo/
        * ssh-keygen -t rsa
    2. Define the database password in [dbpass](./resources/dbpass)
3. Create test database
    1. Create database stpp
    2. Create schema "test"
    3. Exec query [testdb.sql](./setup/testdb.psql)
5. Run tests
    1. Start server with [common.py](./resources/common.py)
    2. Via pycharm -> right click [test folder](/test) -> 'Run unittests in test'