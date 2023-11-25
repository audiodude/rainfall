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
      cy.visit('/sites');
    });

    it('navigates to home', () => {
      cy.url().should('eq', 'http://localhost:4173/');
    });
  });

  describe('where there is a logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user_welcomed.json',
      });
      let count = 0;
      cy.intercept('GET', 'api/v1/site/list', (req) => {
        if (count === 0) {
          count++;
          req.reply((res) => {
            res.send({ statusCode: 200, fixture: 'sites.json' });
          });
        } else {
          req.reply((res) => {
            res.send({ statusCode: 200, fixture: 'sites-2.json' });
          });
        }
      });
      cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', {
        fixture: 'site.json',
      }).as('load-site');
      cy.intercept('POST', 'api/v1/site', {
        status: 204,
      }).as('new-site');
      cy.visit('/sites');
    });

    it('displays the current sites', () => {
      cy.get('.site-name').contains('My Cool Site');
      cy.get('.site-name').contains('Another Cool Site');
    });

    describe('when a new site is added', () => {
      beforeEach(() => {
        cy.get('#new-site').click().type('A New Site');
        cy.get('#new-button').click();
      });

      it('sends a POST request', () => {
        cy.get('@new-site')
          .its('request.body')
          .should('deep.equal', {
            site: {
              name: 'A New Site',
            },
          });
      });

      it('shows the new site', () => {
        cy.get('.site-name').contains('A New Site');
      });
    });

    it('goes to the edit page when the pencil is clicked', () => {
      cy.get('.edit-site-button').first().click();
      cy.wait('@load-site');
      cy.url().should('eq', 'http://localhost:4173/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
    });
  });
});
