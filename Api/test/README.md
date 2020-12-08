# Instructions

1. Create venv with [dependencies](./dependencies.py)
2. Generate rsa keys, put them in [/test](.) ([public.pem](./public.pem), [private.key](./private.key))
    * https://travistidwell.com/jsencrypt/demo/
    * ssh-keygen -t rsa
3. Create test database
    1. Create database stpp
    2. Create schema "test"
    3. Exec query [testdb.sql](./testdb.psql)
4. Define db password in [dbpass](./dbpass)
5. Run tests