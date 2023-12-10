# Rainfall
Free Bandcamp exodus tool, letting you publish music sites to Netlify using [Faircamp](https://codeberg.org/simonrepp/faircamp).

[![GitHub build status](https://github.com/audiodude/rainfall/actions/workflows/ci.yml/badge.svg)
![codecov](https://codecov.io/gh/audiodude/rainfall/graph/badge.svg?token=rTPXFzOytM)](https://codecov.io/gh/audiodude/rainfall)
![GitHub License](https://img.shields.io/github/license/audiodude/rainfall)

This project does not aim to replicate the full feature set of the Bandcamp site/app. Instead, the goal is to allow artists to create individual websites where users can listen to and potentially download and pay for their tracks. These websites are created using the Faircamp static site generator, and can be hosted anywhere on the web.

Rainfall has reached version 1.0 of development!

![image](https://github.com/audiodude/rainfall/assets/57832/04e7088a-3d61-4dcd-b22a-445be161534e)

Currently, you can upload tracks and preview your Faircamp powered site. When you're ready, you can download a .ZIP file of your site, which you can then upload it to any of the cloud providers mentioned on the welcome page, or anywhere else that hosts static websites:

* [Netlify](https://www.netlify.com/)
* [Google Cloud](https://cloud.google.com/storage?hl=en)
* [Amazon Web Services](https://aws.amazon.com/s3/)
* [Render](https://render.com)
* [Cloudflare Pages](https://pages.cloudflare.com/)
* And many others!


Future plans are to integrate with these providers, specifically [Netlify](https://www.netlify.com/), so that you can immediately upload your new website and host it for free under an account that you control. Even more future integrations might  allow you to purchase a domain name through Netlify and go from zero -> running music site with just a few uploads.

## Development

Rainfall features a [Python](https://www.python.org/) backend, using the amazing [Flask](https://flask.readthedocs.io/) API framework and the [SQLAlchemy](https://www.sqlalchemy.org/) ORM (which is much less scary than it seems at first). The database system is [SQLite](https://www.sqlite.org/index.html).  It is tested using [Pytest](https://pytest.org/).

The frontend is written in [Vue 3](https://vuejs.org/) using the Options API, with frontend styling implemented using [TailwindCSS](https://tailwindcss.com/) and some [Flowbite](https://flowbite.com/) components. It is tested using [Cypress](https://www.cypress.io/).

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

The docker container will automatically be built remotely and deployed. The backend data for the production site (SQLite db and song/project files) lives on a Fly volume that is attached to the web worker.
