describe('Edit Release test', () => {
  describe('when there is no logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 401,
        body: {
          status: 401,
          error: 'No signed in user',
        },
      }).as('load-user');
      cy.visit('/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42');
      cy.wait('@load-user');
    });

    it('navigates to home', () => {
      cy.url().should('eq', 'http://localhost:4173/');
    });
  });

  describe('when there is an unwelcomed user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user.json',
      }).as('load-user');
      cy.visit('/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42');
      cy.wait('@load-user');
    });

    it('navigates to welcome', () => {
      cy.url().should('eq', 'http://localhost:4173/welcome');
    });
  });

  describe('when there is a welcomed user', () => {
    let requestNonce: string | number;

    describe('and the release is empty', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/user', {
          fixture: 'user_welcomed.json',
        }).as('load-user');
        cy.intercept('GET', 'api/v1/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42', {
          fixture: 'release-empty.json',
        }).as('load-release');
        cy.intercept(
          'GET',
          'api/v1/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42/artwork?nonce=*',
          (req) => {
            // Technically we never return a valid JPG for the artwork, but it should be fine.
            requestNonce = req.query.nonce;
            req.reply({ statusCode: 404 });
          },
        ).as('load-artwork');
        cy.visit('/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42');
        cy.wait('@load-user');
        cy.wait('@load-release');
      });

      describe('when the page first loads', () => {
        it('attempts to load artwork', () => {
          cy.wait('@load-artwork');
        });

        it('displays an empty description', () => {
          cy.get('#release-description').should('have.value', '');
        });

        it('has a disabled upload artwork button', () => {
          cy.get('.art-upload-cont').find('.upload-songs-button').should('be.disabled');
        });

        it('has a disabled update description button', () => {
          cy.get('#update-description-button').should('be.disabled');
        });
      });

      describe('when the user selects an artwork file', () => {
        beforeEach(() => {
          cy.get('.art-upload-cont')
            .find('.upload-input')
            .selectFile({
              contents: Cypress.Buffer.from('fake artwork contents, not artwork'),
            });
        });

        it('enables the upload artwork button', () => {
          cy.get('.art-upload-cont').find('.upload-songs-button').should('not.be.disabled');
        });

        describe('when the user clicks the upload artwork button', () => {
          let firstNonce: string | number;
          let secondNonce: string | number;

          beforeEach(() => {
            cy.wait('@load-artwork');
            cy.intercept(
              'POST',
              'api/v1/upload/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42/art',
              (req) => {
                expect(req.body).to.include('artwork');
                req.reply({ statusCode: 201 });
              },
            ).as('upload-artwork');

            firstNonce = requestNonce;
            cy.get('.art-upload-cont').find('.upload-songs-button').click();
          });

          it('uploads the artwork', () => {
            cy.wait('@upload-artwork');
          });

          it('updates the artwork display nonce', () => {
            cy.wait('@upload-artwork');
            expect(firstNonce).to.not.equal(requestNonce);
          });
        });
      });
    });

    describe('and the release is not empty', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/user', {
          fixture: 'user_welcomed.json',
        }).as('load-user');
        cy.intercept('GET', 'api/v1/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42', {
          fixture: 'release-filled.json',
        }).as('load-release');
        cy.intercept(
          'GET',
          'api/v1/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42/artwork?nonce=*',
          (req) => {
            // Technically we never return a valid JPG for the artwork, but it should be fine.
            requestNonce = req.query.nonce;
            req.reply({ statusCode: 404 });
          },
        ).as('load-artwork');
        cy.visit('/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42');
        cy.wait('@load-user');
        cy.wait('@load-release');
      });

      describe('when the page first loads', () => {
        it('attempts to load artwork', () => {
          cy.wait('@load-artwork');
        });

        it('displays the release description', () => {
          cy.get('#release-description').should('have.value', 'This is the description');
        });

        it('has a disabled upload artwork button', () => {
          cy.get('.art-upload-cont').find('.upload-songs-button').should('be.disabled');
        });

        it('has a disabled update description button', () => {
          cy.get('#update-description-button').should('be.disabled');
        });

        it('has a delete release button', () => {
          cy.get('#delete-release-button').should('exist');
        });
      });

      describe('after typing in the description field', () => {
        it('enables the update description button', () => {
          cy.get('#release-description').type(' wow');
          cy.get('#update-description-button').should('not.be.disabled');
        });

        it('disables it again after the text is unchanged', () => {
          cy.get('#release-description').type(' a{backspace}{backspace}');
          cy.get('#update-description-button').should('be.disabled');
        });
      });

      describe('on delete release button click', () => {
        beforeEach(() => {
          cy.intercept('DELETE', 'api/v1/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42', {
            statusCode: 204,
          }).as('delete-release');
          cy.get('#delete-release-button').click();
        });

        it('displays a confirmation dialog', () => {
          cy.get('#delete-modal').should('be.visible');
        });

        it('deletes the release', () => {
          cy.get('#delete-modal').find('.confirm-delete').click();
          cy.wait('@delete-release');
        });

        it('navigates to the site page of the release', () => {
          cy.get('#delete-modal').find('.confirm-delete').click();
          cy.wait('@delete-release');
          cy.url().should('eq', 'http://localhost:4173/site/065f4a1a-cd8a-7d4a-8000-b29784430f23');
        });

        it('closes the modal on cancel', () => {
          cy.get('#delete-modal').find('.cancel-delete').click();
          cy.get('#delete-modal').should('not.be.visible');
        });
      });
    });
  });
});
