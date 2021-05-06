\c candles
create table okb_usdt_1h (
  timestamp bigint primary key,
  open varchar(20) not null,
  high varchar(20) not null,
  low varchar(20) not null,
  close varchar(20) not null,
  vol varchar(32),
  volCcy varchar(32),
  increase float8,
  amplitude float8,
  up float8,
  volatility float8
);

create table okb_usdt_15m (
  timestamp bigint primary key,
  open varchar(20) not null,
  high varchar(20) not null,
  low varchar(20) not null,
  close varchar(20) not null,
  vol varchar(32),
  volCcy varchar(32),
  increase float8,
  amplitude float8,
  up float8,
  volatility float8
);

create table okb_usdt_1m (
  timestamp bigint primary key,
  open varchar(20) not null,
  high varchar(20) not null,
  low varchar(20) not null,
  close varchar(20) not null,
  vol varchar(32),
  volCcy varchar(32),
  increase float8,
  amplitude float8,
  up float8,
  volatility float8
);