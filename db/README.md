

### postgresql

#### start service

    Ubuntu: pg_ctlcluster 13 main start
    MacOS:  brew services start postgresql
            pg_ctl -D /usr/local/var/postgres start

#### lookup

    \du list of roles
    \l  list of databases
    \dt list of relations
    \c database  change database
    \d table_name  table structure

#### command

    # sudo su - postgres -c "createuser jameson"
    # sudo su - postgres -c "createdb candles"
    sudo -u postgres psql
    psql -U postgres
    CREATE ROLE jameson with login password 'volatility' createdb;
    ALTER DEFAULT PRIVILEGES GRANT SELECT ON TABLES TO PUBLIC;
    ALTER DEFAULT PRIVILEGES GRANT INSERT ON TABLES TO jameson;

    sudo -u postgres psql -U postgres -d candles -f create_candles_eth.sql
    sudo -u postgres psql -U postgres candles < create_candles_eth.sql

#### role

    select * from pg_shadow;
    alter user postgres with password 'whocares';

#### dump & restore

    pg_dump -h 127.0.0.1 -U postgres -p 5432 -t okb_usdt_15m -f okb_15.dmp -Fc candles
    pg_restore -h 127.0.0.1 -p 5432 -d candles -v okb_15.dmp

#### problem

    psql: error: FATAL: Peer authentication failed for user "postgres"
    
    sudo vi /etc/postgresql/13/main/pg_ident.conf
    local  all  all  127.0.0.1/32  trust

    sudo pg_ctlcluster 13 main restart