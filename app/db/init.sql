CREATE DATABASE IF NOT EXISTS `demo_fastapi`;
USE `demo_fastapi`;

CREATE TABLE IF NOT EXISTS `users`
(
    `id`           int NOT NULL AUTO_INCREMENT,
    `github_id`    int                                                           DEFAULT NULL,
    `username`     varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
    `avatar_url`   varchar(255)                                                  DEFAULT NULL,
    `profile_url`  varchar(255)                                                  DEFAULT NULL,
    `name`         varchar(100)                                                  DEFAULT NULL,
    `location`     varchar(100)                                                  DEFAULT NULL,
    `email`        varchar(100)                                                  DEFAULT NULL,
    `public_repos` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
    `public_gists` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
    `followers`    int                                                           DEFAULT NULL,
    `following`    int                                                           DEFAULT NULL,
    `created_at`   varchar(50)                                                   DEFAULT NULL,
    `updated_at`   varchar(50)                                                   DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `github_id` (`github_id`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 4
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `todos`
(
    `id`          int          NOT NULL AUTO_INCREMENT,
    `user_id`     int          NOT NULL,
    `title`       varchar(255) NOT NULL,
    `description` text,
    `completed`   tinyint(1)   NOT NULL DEFAULT '0',
    `created_at`  timestamp    NULL     DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  timestamp    NULL     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 2
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

