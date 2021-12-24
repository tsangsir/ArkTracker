create table ark_update_tbl (
	update_id number generated always as identity,
	update_date date,
	fund varchar2(10),
	constraint ark_updates_pk primary key (update_id)
)
organization index
including update_date;

create table ark_holding_tbl (
	update_id number,
	ticker varchar2(10),
	earnings_date date,
	weight number,
	market_cap number,
	market_cap_unit varchar2(10),
	ark_ownership number,
	country varchar2(100),
	constraint ark_holding_pk primary key (update_id, ticker),
	constraint ark_holding_fk1 foreign key (update_id) 
	references ark_update_tbl (update_id)
);

create table ark_trade_tbl (
	trade_id number generated always as identity,
	fund varchar2(10),
	ticker varchar2(10),
	trade_date date,
	direction varchar2(1),
	shares number,
	fund_weight number,
	constraint ark_trade_pk primary key (trade_id, fund, ticker)
);

create index ark_trade_idx1 on ark_trade_tbl (trade_date, ticker);

create table ark_ticker_info_tbl (
	ticker varchar2(10),
	company varchar2(200),
	constraint ark_ticker_info_pk primary key (ticker)
)
organization index
including company;

