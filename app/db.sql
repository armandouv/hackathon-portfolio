DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE users
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT UNIQUE NOT NULL,
    password  TEXT        NOT NULL,
    firstname TEXT        NOT NULL,
    lastname  TEXT        NOT NULL
);

CREATE TABLE post
(
    id_post           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_by        INTEGER   NOT NULL,
    creation_date     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modification_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title             TEXT      NOT NULL,
    text              TEXT      NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users (id)
);