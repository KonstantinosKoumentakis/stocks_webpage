create schema stocks_schema;


drop table if exists stocks_schema.history;
drop table if exists stocks_schema.recommendations;
drop table if exists stocks_schema.tweets;
drop table if exists stocks_schema.s_p_companies;


create table stocks_schema.s_p_companies(
    ticker                      varchar(256) primary key
);


create table stocks_schema.history(
    history_id                  serial primary key,
    ticker                      varchar(256) references stocks_schema.s_p_companies("ticker") on delete cascade on update cascade,
    date                        timestamp without time zone,
    open                        decimal,
    high                        decimal,
    low                         decimal,
    close                       decimal,
    volume                      int,
    dividents                   decimal,
    stock_splits                decimal
);


create table stocks_schema.recommendations(
    recommendation_id           serial primary key,
    ticker                      varchar(256) references stocks_schema.s_p_companies("ticker") on delete cascade on update cascade,
    grade                       varchar(256),
    number_of_firms             int
);


create table stocks_schema.tweets(
    tweet_id                    serial primary key,
    ticker                      varchar(256) references stocks_schema.s_p_companies("ticker") on delete cascade on update cascade,
    text                        varchar(256)
);
