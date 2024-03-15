describe('Welcome Test', () => {
  describe('when there is no logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 401,
        body: {
          status: 401,
          error: 'No signed in user',
        },
      });
    });

    it('navigates to home', () => {
      cy.visit('/welcome');
      cy.url().should('eq', 'http://localhost:4173/');
    });
  });

  describe('when a user is logged in', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user.json',
      });
      cy.visit('/welcome');
    });

    it('displays the checkbox', () => {
      cy.get('input').should('have.attr', 'type', 'checkbox');
    });

    it('disables the button', () => {
      cy.get('button.get-started').should('have.attr', 'disabled');
    });

    it('enables the button when the checkbox is clicked', () => {
      cy.get('input').should('have.attr', 'type', 'checkbox').click();
      cy.get('button.get-started').should('not.have.attr', 'disabled');
    });

    it('requests API for setting welcome when the button is clicked', () => {
      cy.intercept('POST', 'api/v1/user/welcome', cy.spy().as('welcome'));
      cy.get('input').should('have.attr', 'type', 'checkbox').click();
      cy.get('button.get-started').click();
      cy.get('@welcome').should('have.been.calledOnce');
    });

    it('navigates to /sites when the button is clicked', () => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user_welcomed.json',
      });
      cy.intercept('POST', 'api/v1/user/welcome', {
        status: 200,
      });
      cy.intercept('GET', 'api/v1/site/list', { fixture: 'sites.json' }).as('list-sites');
      cy.get('input').should('have.attr', 'type', 'checkbox').click();
      cy.get('button.get-started').click();
      cy.wait('@list-sites');
      cy.url().should('eq', 'http://localhost:4173/sites');
    });
  });
});
