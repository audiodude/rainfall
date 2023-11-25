describe('Edit Site test', () => {
  describe('when there is no logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 404,
        body: {
          status: 404,
          error: 'No signed in user',
        },
      });
      cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
    });

    it('navigates to home', () => {
      cy.url().should('eq', 'http://localhost:4173/');
    });
  });

  describe('when there is an unwelcomed user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user.json',
      });
      cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
    });

    it('navigates to welcome', () => {
      cy.url().should('eq', 'http://localhost:4173/welcome');
    });
  });

  describe('when there is a welcomed user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        fixture: 'user_welcomed.json',
      });

      let count = 0;
      cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', (req) => {
        if (count === 0) {
          count++;
          req.reply((res) => {
            res.send({ statusCode: 200, fixture: 'site.json' });
          });
        } else if (count === 1) {
          count++;
          req.reply((res) => {
            res.send({ statusCode: 200, fixture: 'site-2.json' });
          });
        } else {
          req.reply((res) => {
            res.send({ statusCode: 200, fixture: 'site-3.json' });
          });
        }
      }).as('load-site');
      cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
    });

    it('shows the add release button', () => {
      cy.get('#new-release-button').should('be.visible');
    });

    describe('when the add release button is clicked', () => {
      beforeEach(() => {
        cy.intercept('POST', 'api/v1/release', {
          status: 204,
        }).as('new-release');
        cy.get('#new-release-button').click();
        cy.wait('@load-site');
      });

      it('sends a POST request', () => {
        cy.get('@new-release')
          .its('request.body')
          .should('deep.equal', {
            release: {
              name: `Release 1`,
              site_id: '06547ed8-206f-7d3d-8000-20ab423e0bb9',
            },
          });
      });

      it('displays the newly created release', () => {
        cy.get('.release-name').contains('Release 1');
      });

      describe('when the button is clicked again', () => {
        beforeEach(() => {
          cy.intercept('POST', 'api/v1/release', {
            status: 204,
          }).as('new-release');
          cy.get('#new-release-button').click();
          cy.wait('@load-site');
        });

        it('sends a POST request', () => {
          cy.get('@new-release')
            .its('request.body')
            .should('deep.equal', {
              release: {
                name: `Release 2`,
                site_id: '06547ed8-206f-7d3d-8000-20ab423e0bb9',
              },
            });
        });

        it('displays the newly created release', () => {
          cy.get('.release-name').contains('Release 2');
        });
      });
    });

    describe('when there are two releases', () => {
      let calledUpload = false;
      beforeEach(() => {
        let count = 0;
        cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', (req) => {
          if (count === 0) {
            count++;
            req.reply((res) => {
              res.send({ statusCode: 200, fixture: 'site-3.json' });
            });
          } else if (count === 1) {
            req.reply((res) => {
              res.send({ statusCode: 200, fixture: 'site-4.json' });
            });
          }
        });
        cy.intercept('POST', 'api/v1/upload', (req) => {
          calledUpload = true;
          req.reply(204, '', {});
        }).as('upload-songs');
        cy.fixture('song.json').as('song');
      });

      it(`doesn't allow you to click Upload Songs without selecting a file`, () => {
        cy.get('.upload-songs-button').should('be.disabled');
      });

      describe('when a file is selected for release 1', () => {
        beforeEach(() => {
          cy.get('.upload-input').first().selectFile('@song');
        });

        it('enables the corresponding upload button', () => {
          cy.get('.upload-songs-button').first().should('not.be.disabled');
        });

        it('does not enable the other upload button', () => {
          cy.get('.upload-songs-button').eq(1).should('be.disabled');
        });

        describe('when the upload button is clicked', () => {
          beforeEach(() => {
            cy.get('.upload-songs-button').first().click();
          });

          it('uploads the song', () => {
            cy.wait('@upload-songs').then(() => {
              cy.wrap(calledUpload).should('eq', true);
            });
          });

          it('displays the new song', () => {
            cy.wait('@upload-songs').then(() => {
              cy.get('.file-name').contains('song-1.mp3');
            });
          });
        });
      });
    });
  });
});
