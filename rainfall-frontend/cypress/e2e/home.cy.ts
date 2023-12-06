describe('Home Test', () => {
  describe('when there is no logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 404,
        body: {
          status: 404,
          error: 'No signed in user',
        },
      });
      cy.visit('/');
    });

    it('shows the marketing copy', () => {
      cy.contains('div', 'Your music. Your website. Your way.');
    });

    it('shows the sign in div', () => {
      cy.contains('div', 'Sign in with Google');
    });

    it(`doesn't have a signed in user in the nav bar`, () => {
      cy.contains('Not signed in');
    });
  });

  describe('when a user is logged in', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user.json',
      });
      cy.visit('/');
    });

    it('shows the user email in the nav bar', () => {
      cy.get('nav').contains('foo@email.fake');
    });

    it('shows the user picture in the nav bar', () => {
      cy.get('.user-state')
        .find('img')
        .should('have.attr', 'src', 'https://lh3.googleusercontent.fake/photo-12345');
    });

    it('logs them out when they click sign out', () => {
      cy.intercept('GET', 'api/v1/logout', cy.spy().as('logout'));
      cy.get('button.sign-out').click();
      cy.get('@logout').should('have.been.calledOnce');
    });
  });
});
