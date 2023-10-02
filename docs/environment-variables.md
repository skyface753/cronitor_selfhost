# Environment

| Variable               | Description                                                              | Required               | Default                                                            |
| ---------------------- | ------------------------------------------------------------------------ | ---------------------- | ------------------------------------------------------------------ |
| APIKEY                 | The API key to inject results                                            | true                   |                                                                    |
| MAIL_DISABLED          | Disable sending emails (primarily for testing)                           | false                  | false                                                              |
| CLIENT_URL             | The url of the frontend (for cors)                                       | false                  | [SAME-SITE]                                                        |
| MONGODB_CONNECTION_URI | The MongoDB connection URI                                               | false                  | mongodb://admin:admin@127.0.0.1:27017/jobs_db_dev?authSource=admin |
| DB_NAME                | The MongoDB database name (should be the same as MONGODB_CONNECTION_URI) | false                  | jobs_db_dev                                                        |
| COLL_NAME              | The MongoDB collection name                                              | false                  | job_results                                                        |
| SMTP_HOST              | The SMTP host                                                            | IF MAIL_DISABLED=false |                                                                    |
| SMTP_PORT              | The SMTP port                                                            | IF MAIL_DISABLED=false |                                                                    |
| SMTP_USERNAME          | The SMTP username                                                        | IF MAIL_DISABLED=false |                                                                    |
| SMTP_PASSWORD          | The SMTP password                                                        | IF MAIL_DISABLED=false |                                                                    |
| SMTP_FROM              | The sender address of the emails                                         | IF MAIL_DISABLED=false |                                                                    |
| SMTP_TO                | The receiver address of the emails                                       | IF MAIL_DISABLED=false |                                                                    |
| SHOW_DOCS              | Show the docs at /api/v1/docs and /api/v1/redocs                         | false                  | false                                                              |
