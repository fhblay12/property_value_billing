create table if not exists admin_login
(
    admin_login_id char(36) not null primary key default (UUID()),
    admin_username varchar(20)  not null,
    admin_password varchar(20)  not null,
    admin_role     varchar(255) null
);

create table if not exists attendance
(
    id                char(36) not null primary key default (UUID()),
    collector_id_code varchar(50) null,
    check_in          datetime    null,
    check_out         datetime    null
);

create table if not exists category
(
    category_id char(36) not null primary key,
    category    varchar(255) not null
);

create table if not exists collectors
(
    collector_id           char(36) not null primary key default (UUID()),
    collector_id_code      varchar(255)         not null,
    collector_first_name   varchar(255)         not null,
    collector_last_name    varchar(255)         not null,
    collector_phone_number varchar(255)         not null,
    collector_email        varchar(255)         not null,
    collector_password     varchar(255)         not null,
    at_work                tinyint(1) default 0 not null,
    qr_token               varchar(100)         null,
    qr_token_expiration    datetime             null,
    constraint qr_token
        unique (qr_token)
);

create table if not exists contacts
(
    owner_id         char(36) not null primary key,
    first_name       varchar(255) not null,
    last_name        varchar(255) not null,
    phone_number     varchar(20)  not null,
    email            varchar(255) not null,
    created_datetime datetime     not null,
    updated_datetime datetime     not null,
    password         varchar(20)  not null,
    constraint uq_contacts_email unique (email)
);

create table if not exists filetype
(
    filetype_id char(36) not null primary key,
    filetype    varchar(255) not null
);

create table if not exists properties
(
    property_id      char(36) not null primary key,
    category_id      char(36) not null,
    property_value   int            not null,
    owner_id         char(36) not null,
    longitude        decimal(10, 7) not null,
    latitude         decimal(10, 7) not null,
    digital_address  varchar(255)   not null,
    city             varchar(255)   not null,
    description      blob           null,
    created_datetime datetime       not null,
    updated_datetime datetime       null,
    constraint properties_category__fk
        foreign key (category_id) references category (category_id),
    constraint properties_contacts_owner_id_fk
        foreign key (owner_id) references contacts (owner_id)
);

create table if not exists billing
(
    billing_id       char(36) not null primary key default (UUID()),
    monthly_bill     decimal(10, 2)       not null,
    property_id      char(36)             not null,
    created_datetime datetime             not null,
    updated_datetime datetime             null,
    billing_date     datetime             not null,
    has_been_paid    tinyint(1) default 0 not null,
    payment_date     datetime             null,
    constraint billing_ibfk_1
        foreign key (property_id) references properties (property_id)
);

create index billing_property_id_idx
    on billing (property_id);

create table if not exists files
(
    file_id          char(36) not null primary key default (UUID()),
    property_id      char(36)         not null,
    file_data        longblob     not null,
    filename         varchar(255) not null,
    filetype_id      char(36)         not null,
    created_datetime datetime     not null,
    updated_datetime datetime     null,
    constraint files_filetype_filetype_id_fk
        foreign key (filetype_id) references filetype (filetype_id),
    constraint files_ibfk_1
        foreign key (property_id) references properties (property_id)
);

create index files_property_id_idx
    on files (property_id);

create table if not exists test_billing
(
    billing_id   char(36) not null primary key default (UUID()),
    property_id  char(36) not null,
    monthly_bill int      null,
    billing_date datetime not null
);

insert ignore into admin_login (admin_login_id, admin_username, admin_password, admin_role)
values
    ('00000000-0000-0000-0000-000000000000', 'admin', 'admin', 'admin');

insert ignore into category (category_id, category)
values
    ('11111111-1111-1111-1111-111111111111', 'Residential'),
    ('22222222-2222-2222-2222-222222222222', 'Commercial');

insert ignore into filetype (filetype_id, filetype)
values
    ('33333333-3333-3333-3333-333333333333', 'image'),
    ('44444444-4444-4444-4444-444444444444', 'document');

-- Sample contacts (property owners)
insert ignore into contacts (owner_id, first_name, last_name, phone_number, email, created_datetime, updated_datetime, password)
values
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'John', 'Doe', '0501234567', 'john.doe@example.com', NOW(), NOW(), 'pass123'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Jane', 'Smith', '0559876543', 'jane.smith@example.com', NOW(), NOW(), 'pass456'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Alice', 'Johnson', '0541111111', 'alice.j@example.com', NOW(), NOW(), 'pass789');

-- Sample properties
insert ignore into properties (property_id, category_id, property_value, owner_id, longitude, latitude, digital_address, city, description, created_datetime, updated_datetime)
values
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111', 250000, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', -0.1969, 5.5520, 'GA-123-4567', 'Accra', 'Modern residential apartment', NOW(), NOW()),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '22222222-2222-2222-2222-222222222222', 500000, 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', -0.2029, 5.5589, 'GA-234-5678', 'Accra', 'Commercial office space', NOW(), NOW()),
    ('ffffffff-ffff-ffff-ffff-ffffffffffff', '11111111-1111-1111-1111-111111111111', 180000, 'cccccccc-cccc-cccc-cccc-cccccccccccc', -0.1839, 5.5480, 'GA-345-6789', 'Accra', 'Residential townhouse', NOW(), NOW());

-- Sample billing records
insert ignore into billing (billing_id, monthly_bill, property_id, created_datetime, updated_datetime, billing_date, has_been_paid, payment_date)
values
    ('aaaa0001-0001-0001-0001-0001000000aa', 1250.50, 'dddddddd-dddd-dddd-dddd-dddddddddddd', NOW(), NOW(), '2026-06-01', 1, '2026-06-05'),
    ('bbbb0001-0001-0001-0001-0001000000bb', 2500.00, 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', NOW(), NOW(), '2026-06-01', 0, NULL),
    ('cccc0001-0001-0001-0001-0001000000cc', 900.75, 'ffffffff-ffff-ffff-ffff-ffffffffffff', NOW(), NOW(), '2026-06-01', 1, '2026-06-10'),
    ('aaaa0002-0002-0002-0002-0002000000aa', 1250.50, 'dddddddd-dddd-dddd-dddd-dddddddddddd', NOW(), NOW(), '2026-05-01', 1, '2026-05-08');

-- Sample collectors
insert ignore into collectors (collector_id, collector_id_code, collector_first_name, collector_last_name, collector_phone_number, collector_email, collector_password, at_work)
values
    ('11110000-0000-0000-0000-000000000001', 'COL001', 'Samuel', 'Mensah', '0501111111', 'samuel.m@example.com', 'pass123', 1),
    ('22220000-0000-0000-0000-000000000002', 'COL002', 'Ama', 'Sarpong', '0502222222', 'ama.s@example.com', 'pass456', 0);
