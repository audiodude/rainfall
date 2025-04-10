# Rainfall

Free Bandcamp exodus tool, letting you publish music sites to Netlify using [Faircamp](https://codeberg.org/simonrepp/faircamp).

![GitHub build status](https://github.com/audiodude/rainfall/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/audiodude/rainfall/branch/main/graph/badge.svg?token=rTPXFzOytM)](https://codecov.io/gh/audiodude/rainfall)
![GitHub License](https://img.shields.io/github/license/audiodude/rainfall)

This project does not aim to replicate the full feature set of the Bandcamp site/app. Instead, the goal is to allow artists to create individual websites where users can listen to and potentially download and pay for their tracks. These websites are created using the Faircamp static site generator, and can be hosted anywhere on the web.

Rainfall has reached [version 1.5](https://sfba.social/@audiodude/113784434545357783) of development!

![Screenshot of the Rainfall tool, on the song upload page](https://github.com/audiodude/rainfall/assets/57832/04e7088a-3d61-4dcd-b22a-445be161534e)

Currently, you can upload tracks and preview your Faircamp powered site. When you're ready, you can upload your site [directly to Netlify](https://www.netlify.com/), using an OAuth integration. Alternately, you can download a .ZIP file of your site, which you can then upload to any of the cloud providers mentioned on the welcome page, or anywhere else that hosts static websites:

- [Netlify](https://www.netlify.com/)
- [Google Cloud](https://cloud.google.com/storage?hl=en)
- [Amazon Web Services](https://aws.amazon.com/s3/)
- [Render](https://render.com)
- [Cloudflare Pages](https://pages.cloudflare.com/)
- And many others!

Future integrations might allow you to purchase a domain name through Netlify and go from zero -> running music site with just a few uploads.

## Development

Rainfall features a [Python](https://www.python.org/) backend, using the amazing [Flask](https://flask.readthedocs.io/) API framework and the [SQLAlchemy](https://www.sqlalchemy.org/) ORM (which is much less scary than it seems at first). The database system is [MariaDB](https://mariadb.com/), though early versions used [SQLite](https://www.sqlite.org/index.html). It is tested using [Pytest](https://pytest.org/).

The frontend is written in [Vue 3](https://vuejs.org/) using the Options API, with frontend styling implemented using [TailwindCSS](https://tailwindcss.com/) and some [Flowbite](https://flowbite.com/) components. It is tested using [Cypress](https://www.cypress.io/).

For development, you will need a `.env` file in the project root directory, and a `.env.development` file in the `rainfall-frontend` directory. The project directory may also contain a `.env.prod` file, but this is never loaded, it is purely for reference. Production environment variables are set using [Fly.io secrets](https://fly.io/docs/reference/secrets/).

### Dev services (Docker compose)

The file `docker-compose-dev.yml` contains a MariaDB instance and a Redis instance for use by the development environment. Start them with:

```
docker compose -f docker-compose-dev.yml up -d
```

#### Celery workers

Rainfall uses [Celery](http://docs.celeryq.dev/en/stable/) for generating site previews in the background. For development, you can launch a dev worker from any command line with:

```
pipenv run celery -A rainfall.main worker -l INFO
```

### Running Tests

#### Backend

From the project root, run:

```bash
RAINFALL_ENV=test pipenv run pytest
```

#### Frontend

From the `rainfall-frontend` directory, run:

```bash
yarn run test:e2e:dev
```

## Deployment

Rainfall is deployed to [Fly.io](https://fly.io/) using a Docker container. Once you have installed [flyctl](https://fly.io/docs/hands-on/install-flyctl/) and authenticated, simply run the following:

```bash
fly deploy
```

The frontend (`./rainfall-frontend`, NOT the root directory or Flask app) also requires a `.env.production` file with the fields `GOOGLE_CLIENT_ID` and `VITE_GOOGLE_REDIRECT_URI`. This will be ignored by git, but needs to be present when `fly deploy` is run so that it is baked into the frontend production deployment.

The Docker container will automatically be built remotely and deployed. The backend data for the production site (song/project files) lives in [Minio](https://min.io/), which is also hosted on Fly.io as a separate app.

### Running Database migrations

First, make sure the web app is running (not sleeping) by visiting the Rainfall homepage ([https://rainfall.dev](https://rainfall.dev)).

Then, log into the machine using fly ssh (first setting it up with a key if you need to):

```bash
fly ssh console
```

Finally run the alembic command:

```bash
pipenv run alembic upgrade head
```
