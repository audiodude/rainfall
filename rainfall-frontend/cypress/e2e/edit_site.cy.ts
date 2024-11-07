describe('Edit Site test', () => {
  describe('when there is no logged in user', () => {
    beforeEach(() => {
      cy.intercept('GET', 'api/v1/user', {
        statusCode: 401,
        body: {
          status: 401,
          error: 'No signed in user',
        },
      }).as('load-user');
      cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
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
    });

    // describe('deleting the site', () => {
    //   beforeEach(() => {
    //     cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', {
    //       fixture: 'site.json',
    //     }).as('load-site');
    //     cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
    //     cy.wait('@load-site');
    //   });

    //   it('shows the delete button', () => {
    //     cy.get('#delete-site-button').should('be.visible');
    //   });
    // });

    describe('when there is one release', () => {
      beforeEach(() => {
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
        cy.wait('@load-site');
      });

      it('shows the add release button', () => {
        cy.get('#new-release-button').should('be.visible');
      });

      it('shows the preview button', () => {
        cy.get('#preview-site-button').should('be.visible');
      });

      it('has the preview button disabled when there are no releases', () => {
        cy.get('#preview-site-button').should('be.disabled');
      });

      it('starts with the add release button disabled', () => {
        cy.get('#new-release-button').should('be.disabled');
      });

      describe('when a release is added', () => {
        beforeEach(() => {
          cy.intercept('POST', 'api/v1/release', {
            status: 204,
          }).as('new-release');
          cy.get('#new-release').click().type('Super Cool Stuff');
          cy.get('#new-release-button').click();
          cy.wait('@load-site');
        });

        it('sends a POST request', () => {
          cy.get('@new-release')
            .its('request.body')
            .should('deep.equal', {
              release: {
                name: `Super Cool Stuff`,
                site_id: '06547ed8-206f-7d3d-8000-20ab423e0bb9',
              },
            });
        });

        it('displays the newly created release', () => {
          cy.get('.release-name').contains('Super Cool Stuff');
        });

        describe('when the button is clicked again', () => {
          beforeEach(() => {
            cy.intercept('POST', 'api/v1/release', {
              status: 204,
            }).as('new-release');
            cy.get('#new-release').click().clear().type('Release 2');
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
    });

    describe('when there are two releases', () => {
      let calledUpload = false;
      beforeEach(() => {
        let cnt = 0;
        cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', (req) => {
          if (cnt === 0) {
            cnt++;
            req.reply((res) => {
              res.send({ statusCode: 200, fixture: 'site-3.json' });
            });
          } else if (cnt === 1) {
            req.reply((res) => {
              res.send({ statusCode: 200, fixture: 'site-4.json' });
            });
          }
        }).as('load-site');
        cy.intercept('POST', 'api/v1/upload/**', (req) => {
          calledUpload = true;
          req.reply(204, '', {});
        }).as('upload-songs');
        cy.intercept('GET', 'api/v1/preview/**', (req) => {
          req.reply(204, '', {});
        });
        cy.fixture('song.json').as('song');
        cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
        cy.wait('@load-site');
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

    describe('when there is a release with an upload', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/user', {
          fixture: 'user_welcomed.json',
        });
        cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', {
          fixture: 'site-4.json',
        }).as('load-site');
        cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
        cy.wait('@load-site');
      });

      it('has the preview button enabled', () => {
        cy.get('#preview-site-button').should('not.be.disabled');
      });

      describe('when the preview button is clicked', () => {
        let calledPreview = false;
        beforeEach(() => {
          cy.intercept('POST', 'api/v1/preview/06547ed8-206f-7d3d-8000-20ab423e0bb9', (req) => {
            calledPreview = true;
            req.reply(204, '', {});
          }).as('preview-site');
          cy.get('#preview-site-button').click();
        });

        it('calls the preview endpoint', () => {
          cy.wait('@preview-site');
          cy.wrap(calledPreview).should('eq', true);
        });

        it('shows a loading message', () => {
          cy.get('.preview-load').find('.loader').should('be.visible');
          cy.get('.preview-load').should('not.contain', 'Open preview in new window');
        });

        it('shows the preview link', () => {
          cy.wait('@preview-site');
          cy.get('.preview-load').contains('Open preview in new window');
        });

        it('has the right URL for the preview link', () => {
          cy.wait('@preview-site');
          cy.get('.preview-link')
            .should('have.attr', 'href')
            .should('not.be.empty')
            .and('contain', '/preview');
        });
      });

      describe('and the delete button is successfully pressed for one of the files', () => {
        let calledDelete = false;
        beforeEach(() => {
          cy.intercept('DELETE', 'api/v1/file/06552cb9-7fe0-7723-8000-82163fc21234', (req) => {
            calledDelete = true;
            req.reply(204, '', {});
          }).as('delete-song');
          cy.get('.file-name').contains('song-2.mp3').siblings('button').click();
        });

        it('calls the delete endpoint', () => {
          cy.wait('@delete-song');
          cy.wrap(calledDelete).should('eq', true);
        });

        it('removes the file from the list', () => {
          cy.get('.file-name').contains('song-2.mp3').should('not.exist');
        });
      });

      describe('and the delete button is successfully pressed for the last file in the list', () => {
        let calledDelete = false;
        beforeEach(() => {
          cy.intercept('DELETE', 'api/v1/file/06552cb9-7fe0-7723-8000-82163fc25478', (req) => {
            calledDelete = true;
            req.reply(204, '', {});
          }).as('delete-song');
          cy.get('.file-name').contains('a-great-song.mp3').siblings('button').click();
        });

        it('calls the delete endpoint', () => {
          cy.wait('@delete-song');
          cy.wrap(calledDelete).should('eq', true);
        });

        it('removes the file from the list', () => {
          cy.get('.file-name').contains('a-great-song.mp3').should('not.exist');
        });

        it('shows the "no files" message', () => {
          cy.get('.no-files-msg').should('be.visible');
        });
      });

      describe('and the delete call returns an error', () => {
        let calledDelete = false;
        beforeEach(() => {
          cy.intercept('DELETE', 'api/v1/file/06552cb9-7fe0-7723-8000-82163fc21234', (req) => {
            calledDelete = true;
            req.reply(500, '', {});
          }).as('delete-song');
          cy.get('.file-name').contains('song-2.mp3').siblings('button').click();
        });

        it('calls the delete endpoint', () => {
          cy.wait('@delete-song');
          cy.wrap(calledDelete).should('eq', true);
        });

        it('leaves the file in the list', () => {
          cy.get('.file-name').contains('song-2.mp3').should('be.visible');
        });
      });

      describe('and the user clicks the release delete button', () => {
        beforeEach(() => {
          cy.intercept('DELETE', 'api/v1/release/06552cb9-0c60-7066-8000-3c3da08a9e9d', {
            statusCode: 204,
          }).as('delete-release');
          cy.get('.delete-release-overview-button').first().click();
        });

        it('displays a confirmation dialog', () => {
          cy.get('.delete-modal').should('be.visible');
        });

        // There are multiple modals on the page, one for each release and one for the site.
        // We hardcode the index here to select the correct modal.
        it('deletes the release', () => {
          cy.get('.delete-modal').first().find('.confirm-delete').click();
          cy.wait('@delete-release');
        });

        it('reloads the site with the release removed', () => {
          cy.get('.delete-modal').first().find('.confirm-delete').click();
          cy.wait('@delete-release');
          cy.wait('@load-site');
        });

        it('closes the modal on cancel', () => {
          cy.get('.delete-modal').first().find('.cancel-delete').click();
          cy.get('.delete-modal').first().should('not.be.visible');
        });

        it('closes the modal on close button click', () => {
          cy.get('.delete-modal').first().find('.close-modal-button').click();
          cy.get('.delete-modal').first().should('not.be.visible');
        });

        it('closes the modal on background click', () => {
          cy.get('#app').click('topLeft');
          cy.get('.delete-modal').first().should('not.be.visible');
        });
      });
    });

    describe('editing name', () => {
      beforeEach(() => {
        cy.intercept('GET', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9', {
          fixture: 'site.json',
        }).as('load-site');
        cy.visit('/site/06547ed8-206f-7d3d-8000-20ab423e0bb9');
        cy.wait('@load-site');
      });

      it('shows the disabled edit name button on load', () => {
        cy.get('#edit-name-button').should('be.disabled');
      });

      describe('when the name is changed', () => {
        beforeEach(() => {
          cy.get('#site-name').type('{selectAll}{backspace}');
          cy.get('#site-name').type('New name');
        });

        it('enables the edit name button when the name is changed', () => {
          cy.get('#edit-name-button').should('not.be.disabled');
        });

        it('sends a POST request when the button is clicked', () => {
          cy.intercept('POST', 'api/v1/site/06547ed8-206f-7d3d-8000-20ab423e0bb9/name', {
            status: 204,
          }).as('edit-name');
          cy.get('#edit-name-button').click();
          cy.wait('@edit-name').then((req) => {
            expect(req.request.body).to.deep.equal({
              name: 'New name',
            });
          });
        });

        it('disables the button again if the name returns to the original value', () => {
          cy.get('#site-name').type('{selectAll}{backspace}');
          cy.get('#site-name').type('My Cool Site');
          cy.get('#edit-name-button').should('be.disabled');
        });
      });
    });
  });
});
