# Testing

## [Setup](./setup)
1. Create venv with [dependencies](./setup/dependencies.py)
2. Create [resources](./resources)
    1. Generate rsa keys ( https://travistidwell.com/jsencrypt/demo/ or `ssh-keygen -t rsa`)
        1. [public.pem](./resources/public.pem) and [private.key](./resources/private.key)
        2. [private_invalid.key](./resources/private_invalid.key) and [public_invalid.pem](./resources/public_invalid.pem)
    2. Define the database password in [dbpass](./resources/dbpass)
    2. [Config file](./resources/config.ini) (see [app.config.ini](../app/config.ini))
3. Create test database
    1. Create database stpp
    2. Create schema "test"
    3. Exec query [testdb.sql](./setup/testdb.psql)
5. Run tests
    1. Start server with [common.py](./resources/common.py)
    2. Via pycharm -> right click [test folder](/test) -> 'Run unittests in test'