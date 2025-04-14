# CHANGELOG


## v0.8.2 (2025-04-14)

### Chores

- Add bunster to go special cases
  ([`6ef2d63`](https://github.com/timmyb824/one-updater/commit/6ef2d63f9c3aacf90d94f3d7c21ccd5519b5cf6d))


## v0.8.1 (2025-04-11)

### Chores

- Add yamlfmt go package to the special case dict
  ([`fbf49a9`](https://github.com/timmyb824/one-updater/commit/fbf49a9abc2cbdfbe00ac8d171968dd5b5b844a3))


## v0.8.0 (2025-04-02)

### Features

- Add script for building and release a linux-arm executable
  ([`4032642`](https://github.com/timmyb824/one-updater/commit/40326429e2d2ba5a5e8ebfbdb23d81d6325ba776))

### Refactoring

- Change default config to have brew and apt as they are the most common package managers
  ([`57b3cf8`](https://github.com/timmyb824/one-updater/commit/57b3cf8faa3a0d9310897eb03fc2b842d444c572))


## v0.7.2 (2025-02-21)

### Documentation

- Update release workflow with installation note for executables
  ([`2772bd4`](https://github.com/timmyb824/one-updater/commit/2772bd401f7493010c01edf46f074953b710c3d6))


## v0.7.1 (2025-02-21)

### Continuous Integration

- Add Python setup and install uv in release workflow
  ([`6f495e9`](https://github.com/timmyb824/one-updater/commit/6f495e99dd265af228e6ce0ceb4f74fd76182fc2))


## v0.7.0 (2025-02-21)

### Chores

- Update one-updater-linux binary
  ([`a7d4ba1`](https://github.com/timmyb824/one-updater/commit/a7d4ba1f4acd87fd3eb79a71a22dbbbd0d14416c))

### Continuous Integration

- Add workflow for building and releasing executables
  ([`2621a24`](https://github.com/timmyb824/one-updater/commit/2621a243b3a64570f4e08b12e4a26e088e5b59d9))

### Features

- Support entering a password when prompted during brew upgrade
  ([`076af7f`](https://github.com/timmyb824/one-updater/commit/076af7f8e1f5a67162351d325190231f6f2d65ea))

### Refactoring

- Rename macos updater to darwin and add newest build
  ([`8cb842e`](https://github.com/timmyb824/one-updater/commit/8cb842e47ca0b4e2d984c2a18e899c359cad2773))


## v0.6.0 (2025-02-19)

### Breaking_change

- Refactor cli to stop using click and use argparse instead
  ([`46472b9`](https://github.com/timmyb824/one-updater/commit/46472b969aad11278ffdc41141951f56e96ebd52))

### Features

- Add support for uv package manager
  ([`444d5f5`](https://github.com/timmyb824/one-updater/commit/444d5f53889ee2972ca6578c5c5d0ced721f7ae1))

- Add version command to show version information
  ([`c24510c`](https://github.com/timmyb824/one-updater/commit/c24510c416894a040554ef17ff65e29d66146cc2))

### Refactoring

- Handle version command before loading config in CLI script
  ([`6135387`](https://github.com/timmyb824/one-updater/commit/6135387ff61e570a872ce581efa5a2d6f15f3323))

- Update project dependencies and script name in pyproject.toml
  ([`5c06ace`](https://github.com/timmyb824/one-updater/commit/5c06aceb992978a173498b5f1770476aa03379a9))


## v0.5.1 (2025-02-19)

### Refactoring

- All changes need to stop using poetry and start using uv
  ([`362563f`](https://github.com/timmyb824/one-updater/commit/362563fff5658a53d94accbb16be26f8ffdd642e))


## v0.5.0 (2025-01-20)

### Bug Fixes

- No such file error using init command with pyinstaller exec
  ([`040c8c2`](https://github.com/timmyb824/one-updater/commit/040c8c21a2978135152a61cd7179c46776c37f2f))

### Features

- Add pre-built executable for Linux in one_updater/bin
  ([`c82a934`](https://github.com/timmyb824/one-updater/commit/c82a934f2a0f9cb87a9f9ff0d1ca39d4427d8980))

- Rename macOS updater binary for consistency
  ([`9d49e25`](https://github.com/timmyb824/one-updater/commit/9d49e258fdc5d8d05eaebfcb692ae8a8fe4288ff))

- Update version to 0.5.0 in pyproject.toml
  ([`454faa6`](https://github.com/timmyb824/one-updater/commit/454faa6e2255872bdc0951432e03ce7a44de8cbe))


## v0.4.9 (2025-01-18)

### Chores

- Sync version with changelog; issue with auto setting version
  ([`f22a251`](https://github.com/timmyb824/one-updater/commit/f22a251b20b171c653d3f900ebc92ce7f58c91e4))


## v0.4.8 (2025-01-18)

### Chores

- Rebuild bin on linux
  ([`d863362`](https://github.com/timmyb824/one-updater/commit/d8633620e56469525c5b9db6268a718cf05e4f6d))


## v0.4.7 (2025-01-18)

### Bug Fixes

- Update version to 0.4.6 in pyproject.toml
  ([`a6673fa`](https://github.com/timmyb824/one-updater/commit/a6673fa5f2bd863d0b3253fb89c1403b79729a84))


## v0.4.6 (2025-01-18)

### Refactoring

- Post commit for updating to poetry 2.0
  ([`5044561`](https://github.com/timmyb824/one-updater/commit/5044561ab6c4a78c2cd6d4b5059af59069d1cc55))


## v0.4.5 (2025-01-18)

### Continuous Integration

- Add verbose option for PyPI publish step
  ([`d43d881`](https://github.com/timmyb824/one-updater/commit/d43d88151b77bf8de1e73b465d9898e8418279e8))


## v0.4.4 (2025-01-18)

### Bug Fixes

- Update poetry version to 2.0.0 in CI workflow. Fix binary file path renaming
  ([`32071a4`](https://github.com/timmyb824/one-updater/commit/32071a49f741d5f2d290591a8fcad807656abcfd))

### Chores

- Update dependencies and exclude build files from version control
  ([`2600d59`](https://github.com/timmyb824/one-updater/commit/2600d59aaa9724d8f6132df3e40f26869764d903))


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
