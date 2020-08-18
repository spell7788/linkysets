# Linkysets

Linkysets is a web application that makes possible to create sets of entries of different types in a way of posting a URL of content.

| Entry type | Mime type(s) |
| --- | --- |
| URL | `text/html` |
| Image | `image/jpeg` `image/png` `image/gif` `image/webp` |
| Audio | `audio/wav` `audio/mpeg` `audio/mp4` `audio/aac` `audio/aacp` `audio/ogg` `audio/webm` `audio/flac` |
| Video | `video/mp4` `video/webm` `video/ogg` |
| Youtube video | `text/html` |

## Getting started

### Prerequisites

- [docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

### Installation

Clone the repository:

`git clone https://github.com/hqrrylyu/linkysets.git`

Provide environment variables:

`./envs/local/web.env` or `./envs/production/web.env`

Parsing of web variables is done by [environs](https://github.com/sloria/environs)

```
DJANGO_SETTINGS_MODULE
ALLOWED_HOSTS
SECRET_KEY
DATABASE_URL
```

`./envs/local/db.env` or `./envs/production/db.env`

```
POSTGRES_PASSWORD
```

Run the stack:

`docker-compose up`

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
