describe('New Test', () => {
  describe('when there is no logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 404,
        body: {
          status: 404,
          error: 'No signed in user',
        },
      });
    });

    it('navigates to home', () => {
      cy.visit('/new');
      cy.url().should('eq', 'http://localhost:4173/');
    });
  });
});
