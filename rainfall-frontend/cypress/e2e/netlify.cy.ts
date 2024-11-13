describe('Netlify deploy test', () => {
  describe('when there is no logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 401,
        body: {
          status: 401,
          error: 'No signed in user',
        },
      }).as('load-user');
      cy.visit('/deploy/06547ed8-206f-7d3d-8000-20ab423e0bb9/netlify');
    });

    it('navigates to home', () => {
      cy.wait('@load-user');
      cy.url().should('eq', 'http://localhost:4173/');
    });
  });

  describe('when there is an unwelcomed user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user.json',
      });
      cy.visit('/deploy/06547ed8-206f-7d3d-8000-20ab423e0bb9/netlify');
    });

    it('navigates to welcome', () => {
      cy.url().should('eq', 'http://localhost:4173/welcome');
    });
  });

  describe('where there is a logged in user without a Netlify token', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user_welcomed.json',
      }).as('load-user');
      cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', {
        fixture: 'site.json',
      }).as('load-site');
    });

    describe('but the site preview has not been generated', () => {
      it('navigates to the site edit page', () => {
        cy.visit('/deploy/06547ed8-206f-7d3d-8000-20ab423e0bb9/netlify');
        cy.wait('@load-user');
        cy.wait('@load-site');
        cy.url().should('eq', 'http://localhost:4173/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
      });
    });

    describe('and the site preview has been generated', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/preview//06547ed8-206f-7d3d-8000-20ab423e0bb9', {
          statusCode: 204,
        }).as('load-preview');
        cy.visit('/deploy/06547ed8-206f-7d3d-8000-20ab423e0bb9/netlify');
        cy.wait('@load-user');
        cy.wait('@load-site');
        cy.wait('@load-preview');
      });

      it('displays the connect to Netlify button', () => {
        cy.get('#netlify-connect-button').should('be.visible');
      });

      describe('and the user has no netlify token', () => {
        it('disables the deploy button', () => {
          cy.get('#netlify-deploy-button').should('be.disabled');
        });
      });

      it('sends a POST request when connect to Netlify is clicked', () => {
        cy.on('window:before:load', (win) => {
          // Prevent the page from reloading
          return false;
        });
        cy.log('Setting up intercept');
        cy.intercept('POST', 'api/v1/oauth/netlify/login', { fixture: 'netlify-login.html' }).as(
          'netlify-login',
        );
        cy.log('Clicking connect to Netlify');
        cy.get('#netlify-connect-button').click();
        cy.wait('@netlify-login').then((interception) => {
          const urlSearchParams = new URLSearchParams(interception.request.body);
          expect(urlSearchParams.get('site_id')).to.equal('06547ed8-206f-7d3d-8000-20ab423e0bb9');
        });
      });
    });
    describe('when there is a welcomed user with a Netlify token', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/user', {
          fixture: 'user-welcomed-netlify.json',
        }).as('load-user');

        let count = 0;
        cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', (req) => {
          if (count === 0) {
            req.reply({ fixture: 'site.json' });
          } else {
            req.reply({ fixture: 'site-netlify.json' });
          }
          count++;
        }).as('load-site');
        cy.intercept('GET', 'api/v1/preview//06547ed8-206f-7d3d-8000-20ab423e0bb9', {
          statusCode: 204,
        }).as('load-preview');
        cy.visit('/deploy/06547ed8-206f-7d3d-8000-20ab423e0bb9/netlify');
        cy.wait('@load-user');
        cy.wait('@load-site');
        cy.wait('@load-preview');
      });

      it('enables the deploy button', () => {
        cy.get('#netlify-deploy-button').should('not.be.disabled');
      });

      it('shows the warning message', () => {
        cy.get('#netlify-warning').should('be.visible');
      });

      describe('when the deploy button is clicked', () => {
        it('shows the spinner', () => {
          cy.intercept(
            'POST',
            '/api/v1/oauth/netlify/06547ed8-206f-7d3d-8000-20ab423e0bb9/deploy',
            (req) => {
              cy.get('#netlify-deploy-spinner').should('be.visible');
              req.reply({
                statusCode: 200,
                delay: 750,
                body: { url: 'https://netlify.fake/1234  ' },
              });
            },
          ).as('netlify-deploy');
          cy.get('#netlify-deploy-button').click();
          cy.wait('@netlify-deploy');
        });

        it('shows the URL', () => {
          cy.intercept(
            'POST',
            '/api/v1/oauth/netlify/06547ed8-206f-7d3d-8000-20ab423e0bb9/deploy',
            {
              statusCode: 200,
              body: { url: 'https://netlify.fake/1234' },
            },
          ).as('netlify-deploy');
          cy.get('#netlify-deploy-button').click();
          cy.wait('@netlify-deploy');

          cy.get('#netlify-deploy-result').should('be.visible');
          cy.get('#netlify-deploy-result').should('contain.text', 'https://netlify.fake/1234');
        });
      });
    });
  });
});
