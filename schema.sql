create table wallet_journal
(
    id              bigint unsigned not null    primary key,
    corporation_id  int unsigned    not null,
    ref_type        varchar(128)    not null,
    journal_date    datetime        not null,
    description     varchar(4096)   not null,
    amount          bigint          null,
    reason          varchar(4096)   null,
    first_party_id  int unsigned    null,
    second_party_id int unsigned    null,
    context_id_type varchar(128)    null,
    context_id      bigint unsigned null,
    constraint wallet_journal_id_unique    unique (id)
);
create index wallet_journal_corporation_id_index on wallet_journal (corporation_id);
create index wallet_journal_date_index on wallet_journal (journal_date);
create index wallet_journal_ref_type_index on wallet_journal (ref_type);

create table corporations
(
    id                int               not null   primary key,
    corporation_name  varchar(255)      null,
    character_id      int               not null,
    last_journal_date datetime          null,
    active            tinyint default 1 null,
    constraint corporations_id_unique   unique (id)
);
