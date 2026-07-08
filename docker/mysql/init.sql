USE sentiment;

CREATE TABLE IF NOT EXISTS sentiment_predictions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         VARCHAR(50)  NOT NULL,
    comment         TEXT         NOT NULL,
    sentiment_label VARCHAR(20)  NOT NULL,
    sentiment_score FLOAT        NOT NULL,
    processed_at    DATETIME     NOT NULL
);
