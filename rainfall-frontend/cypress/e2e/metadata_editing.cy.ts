describe('Metadata Editing', () => {
  describe('when there is a welcomed user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user_welcomed.json',
      }).as('load-user');
      cy.intercept('GET', 'api/v1/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42', {
        fixture: 'release-filled.json',
      }).as('load-release');
      cy.visit('/release/065f4a1a-f2e0-7d39-8000-0c3f69747e42');
      cy.wait('@load-user');
      cy.wait('@load-release');
    });

    describe('when viewing a file with metadata', () => {
      it('displays the metadata fields', () => {
        cy.get('.file-name')
          .first()
          .within(() => {
            cy.get('.metadata-title').should('contain', 'Title:');
            cy.get('.metadata-artist').should('contain', 'Artist:');
            cy.get('.metadata-album').should('contain', 'Album:');
          });
      });

      it('shows edit button for metadata', () => {
        cy.get('.file-name').first().find('.edit-button').should('exist');
      });
    });

    describe('when editing metadata', () => {
      beforeEach(() => {
        cy.get('.file-name').first().find('.edit-button').click();
      });

      it('shows input fields for metadata', () => {
        cy.get('.file-name')
          .first()
          .within(() => {
            cy.get('input').should('have.length', 3);
          });
      });

      it('shows save and cancel buttons', () => {
        cy.get('.file-name')
          .first()
          .within(() => {
            cy.get('button').should('contain', 'Save');
            cy.get('button').should('contain', 'Cancel');
          });
      });

      describe('when editing and saving metadata', () => {
        beforeEach(() => {
          cy.intercept('POST', 'api/v1/file/*/metadata', {
            statusCode: 204,
          }).as('save-metadata');

          cy.get('.file-name')
            .first()
            .within(() => {
              cy.get('input').first().clear().type('New Title');
              cy.get('input').eq(1).clear().type('New Artist');
              cy.get('input').eq(2).clear().type('New Album');
              cy.get('button').contains('Save').click();
            });
        });

        it('sends the updated metadata to the server', () => {
          cy.wait('@save-metadata').its('request.body').should('deep.equal', {
            title: 'New Title',
            artist: 'New Artist',
            album: 'New Album',
          });
        });

        it('updates the displayed metadata', () => {
          cy.get('.file-name')
            .first()
            .within(() => {
              cy.get('.metadata-title').should('contain', 'Title:');
              cy.get('.metadata-artist').should('contain', 'Artist:');
              cy.get('.metadata-album').should('contain', 'Album:');
              cy.contains('New Title');
              cy.contains('New Artist');
              cy.contains('New Album');
            });
        });
      });

      describe('when canceling metadata edit', () => {
        beforeEach(() => {
          cy.get('.file-name')
            .first()
            .within(() => {
              cy.get('input').first().clear().type('New Title');
              cy.get('button').contains('Cancel').click();
            });
        });

        it('reverts to original metadata display', () => {
          cy.get('.file-name')
            .first()
            .within(() => {
              cy.get('input').should('not.exist');
              cy.get('.metadata-title').should('contain', 'Title:');
              cy.get('.metadata-artist').should('contain', 'Artist:');
              cy.get('.metadata-album').should('contain', 'Album:');
            });
        });
      });
    });
  });
});
