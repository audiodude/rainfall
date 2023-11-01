# Rainfall
Free alternative to Bandcamp, letting you publish music sites to Netlify using Faircamp.

This project does not aim to replicate the full feature set of the Bandcamp site/app. Instead, the goal is to allow artists to create individual websites where users can listen to and potentially download and pay for their tracks. These websites are created using the [Faircamp](https://codeberg.org/simonrepp/faircamp) static site generator, and can be hosted anywhere on the web.

Rainfall is in a very early stage of development! When finished, it will not only let you upload your tracks and metadata and preview the output website, it will also integrate with [Netlify](https://www.netlify.com/) so that you can immediately upload your new website and host it for free under an account that you control. Further integrations might even allow you to purchase a domain name through Netlify and go from zero -> running music site with just a few uploads. Alternately, we plan to provide a `.zip` download so you can grab your site's code and host it wherever you want. 

## Development

### Running Tests

We use pytest for testing. From the project root, run:

```bash
RAINFALL_ENV=test pipenv run pytest
```
