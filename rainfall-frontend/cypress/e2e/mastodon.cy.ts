describe('Mastodon login test', () => {
  describe('when there is a welcomed user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user_welcomed.json',
      }).as('load-user');
      cy.visit('/mastodon');
    });

    it('navigates to home', () => {
      cy.url().should('eq', 'http://localhost:4173/sites');
    });
  });

  describe('when there is an unwelcomed user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user.json',
      });
      cy.visit('/mastodon');
    });

    it('navigates to welcome', () => {
      cy.url().should('eq', 'http://localhost:4173/welcome');
    });
  });

  describe('when there is no user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 404,
        body: {
          status: 404,
          error: 'No signed in user',
        },
      }).as('load-user');
    });

    describe('and there are no errors', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/mastodon/errors', {
          statusCode: 200,
          body: {
            netloc: '',
            errors: [],
          },
        }).as('errors');
        cy.visit('/mastodon');
        cy.wait('@load-user');
        cy.wait('@errors');
      });

      describe('when no host has been entered', () => {
        it('disables the submit button', () => {
          cy.get('#login-button').should('be.disabled');
        });
      });

      describe('when a host has been entered', () => {
        beforeEach(() => {
          cy.get('#host-input').type('mastodon.pizza.fake');
        });

        it('enables the submit button', () => {
          cy.get('#login-button').should('not.be.disabled');
        });
      });
    });

    describe('and there are errors', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/mastodon/errors', {
          statusCode: 200,
          body: {
            netloc: 'foo.mastodon.fake',
            errors: ['An error occurred, please try again.'],
          },
        }).as('errors');
        cy.visit('/mastodon');
        cy.wait('@load-user');
        cy.wait('@errors');
      });

      it('displays the errors', () => {
        cy.get('#error-list').contains('An error occurred, please try again.');
      });

      it('displays the host', () => {
        cy.get('#host-input').should('have.value', 'foo.mastodon.fake');
      });
    });
  });
});
