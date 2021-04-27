create database candles;
grant all on DATABASE candles to postgres;
\c candles
create table eth_usdt_1h (
  timestamp bigint primary key,
  open varchar(16) not null,
  high varchar(16) not null,
  low varchar(16) not null,
  close varchar(16) not null,
  vol varchar(32),
  volCcy varchar(32),
  increase float8,
  amplitude float8,
  up float8,
  volatility float8
);

create table eth_usdt_15m (
  timestamp bigint primary key,
  open varchar(16) not null,
  high varchar(16) not null,
  low varchar(16) not null,
  close varchar(16) not null,
  vol varchar(32),
  volCcy varchar(32),
  increase float8,
  amplitude float8,
  up float8,
  volatility float8
);