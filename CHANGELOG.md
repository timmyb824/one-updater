# CHANGELOG


## v0.4.3 (2024-12-19)

### Documentation

- Add MIT license
  ([`69f4685`](https://github.com/timmyb824/one-updater/commit/69f4685aec566514610e89d00e6c97e7cb82b4c7))


## v0.4.2 (2024-12-18)

### Bug Fixes

- Add 'sudo' to snap package manager update and upgrade commands
  ([`65b512a`](https://github.com/timmyb824/one-updater/commit/65b512a6868c12242f0f7d0063cd2ac8ef7eb88b))


## v0.4.1 (2024-12-17)

### Refactoring

- Add support for multiple virtualenv; ensure valid pyenv versions still process
  ([`25ee364`](https://github.com/timmyb824/one-updater/commit/25ee3641f3dcfa44327fff2e8436367d73c6939f))


## v0.4.0 (2024-12-02)

### Features

- Add support for multiple pyenv versions in PipManager
  ([`f0bb60c`](https://github.com/timmyb824/one-updater/commit/f0bb60c1ae229a1733d648e4908ec67ba3f18bc3))

### Refactoring

- Configure root logger and handle logging setup more efficiently
  ([`5b72e82`](https://github.com/timmyb824/one-updater/commit/5b72e82fc96994966c597e749a398f52a5b88cbb))

- Ensure valid pyenv versions are still processed instead ofalling back to system version
  ([`0fb3654`](https://github.com/timmyb824/one-updater/commit/0fb365437dd2a8c28d0cb9f7a55189123e63e61a))


## v0.3.1 (2024-12-02)

### Documentation

- Update readme to reflect current state
  ([`54814ab`](https://github.com/timmyb824/one-updater/commit/54814ab3111000b39b7f63eee34f7cd7cdc11123))


## v0.3.0 (2024-11-29)

### Chores

- Black quality changes
  ([`7478b6c`](https://github.com/timmyb824/one-updater/commit/7478b6cd54ceae9794e69c9350e78b214365c3f2))

### Documentation

- Add availability check functions for DNF, Flatpak, and Pacman package managers
  ([`5118f7a`](https://github.com/timmyb824/one-updater/commit/5118f7a6dc1d505d03c3e15afbed561525e383f0))

### Features

- Add DNF, Flatpak, and Pacman package managers
  ([`f75b740`](https://github.com/timmyb824/one-updater/commit/f75b7406d1f9c38fb8fc034699dd43f4c06b2829))

- Add support for pyenv and virtualenv for pip
  ([`aec06cf`](https://github.com/timmyb824/one-updater/commit/aec06cfd03aaa01b9316290e11900544498cb0eb))

- Refactor logging configuration and improve go logic
  ([`ba0bcae`](https://github.com/timmyb824/one-updater/commit/ba0bcaecffc30044cdb4ceba0f8d9793b0cd53d7))


## v0.2.0 (2024-11-25)

### Features

- Add support for entering sudo credentials and pausing status bar
  ([`e231016`](https://github.com/timmyb824/one-updater/commit/e2310162808e307121f223a7826850c070adc36d))


## v0.1.0 (2024-11-25)

### Bug Fixes

- Remove dependancy on the config file when running the version command
  ([`7d0f917`](https://github.com/timmyb824/one-updater/commit/7d0f91741b92c1a9d83074fae32a472eaba2720d))

### Features

- Add init command to create new config file and load default conifg
  ([`5fb9466`](https://github.com/timmyb824/one-updater/commit/5fb9466f8978d91c79e812502f92fbea056ed4dc))


## v0.0.9 (2024-11-25)

### Code Style

- Update command to get version in CI workflow
  ([`e1dcd4c`](https://github.com/timmyb824/one-updater/commit/e1dcd4c3de673649e6f7a06f1415a034ce70147b))

### Documentation

- Update command 'version' help message
  ([`a79a751`](https://github.com/timmyb824/one-updater/commit/a79a75161d89ce6ce3b5ef437185c93c3924d06c))

### Refactoring

- Replace version option with version command
  ([`444a45d`](https://github.com/timmyb824/one-updater/commit/444a45d0b9464e2d06abba57683790d14513711d))


## v0.0.8 (2024-11-25)

### Chores

- Clean up attestation files in CI workflow
  ([`8166eb2`](https://github.com/timmyb824/one-updater/commit/8166eb298f2069e9d9ec8e70d73bbe7b2a485741))


## v0.0.7 (2024-11-25)

### Bug Fixes

- Update GH_TOKEN to use secrets.GITHUB_TOKEN
  ([`ea899a3`](https://github.com/timmyb824/one-updater/commit/ea899a338b9b6595ef622e8d0004571e47268ec7))


## v0.0.6 (2024-11-25)

### Code Style

- Update file listing command in CI workflow to ignore hidden files
  ([`a0c4315`](https://github.com/timmyb824/one-updater/commit/a0c431550447211411119ce0d8c9f59d4180a74a))


## v0.0.5 (2024-11-25)

### Continuous Integration

- Add step to list files in dist folder before publishing to PyPI
  ([`278ddd9`](https://github.com/timmyb824/one-updater/commit/278ddd95a79441d56dbaa24feac30cb697125ff7))


## v0.0.4 (2024-11-25)

### Bug Fixes

- Update environment variable name to match secrets configuration
  ([`8942c88`](https://github.com/timmyb824/one-updater/commit/8942c889ea25037d3a2ca28a6fbbae1bbb6768c7))


## v0.0.3 (2024-11-24)

### Chores

- Update .gitignore to remove build and dist directories
  ([`f8aa478`](https://github.com/timmyb824/one-updater/commit/f8aa47875e48c235797f769f1f8cc5ebd31a1f22))


## v0.0.2 (2024-11-24)

### Code Style

- Update poetry version to 1.8.4 and comment out unnecessary pre-commit hooks
  ([`a381fba`](https://github.com/timmyb824/one-updater/commit/a381fba77ed9efe02fce38e3f0b5263d0429b818))


## v0.0.1 (2024-11-24)

### Build System

- Update Python dependencies to latest versions
  ([`1623f2b`](https://github.com/timmyb824/one-updater/commit/1623f2b316b097928a466d1f324f136b6bb1e938))
