

### postgresql

#### start service

    Ubuntu: pg_ctlcluster 13 main start

#### lookup

    \du list of roles
    \l  list of databases
    \dt list of relations
    \c database  change database
    \d table_name  table structure

#### command

    sudo su - postgres -c "createuser jameson"
    sudo su - postgres -c "createdb candles"
    sudo -u postgres psql
    # grant all privileges on database candles to jameson;
    # ALTER DEFAULT PRIVILEGES GRANT SELECT ON TABLES TO PUBLIC;
    # ALTER DEFAULT PRIVILEGES GRANT INSERT ON TABLES TO jameson;

    sudo -u postgres psql -U postgres -d candles -f create_candles_table.sql
    sudo -u postgres psql -U postgres candles < create_candles_table.sql

#### create/delete

    create database candles;
    drop database candles;
    create user jameson;
    drop user jameson;

#### role

    select * from pg_shadow;
    alter user jameson with password 'volatility';
    alter user postgres with password 'whocares';

#### problemm

    psql: error: FATAL: Peer authentication failed for user "postgres"
    
    sudo vi /etc/postgresql/13/main/pg_ident.conf
    local  all  all  127.0.0.1/32  trust

    sudo pg_ctlcluster 13 main restart