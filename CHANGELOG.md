# Changelog

All notable changes to TruthCheck AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-08

### Added
- **AI Engine**: Integrated core multi-modal deepfake detection pipelines (Spatial, Temporal, Frequency, Compression).
- **Dashboard**: Next.js-based investigative dashboard for reviewing evidence and trust scores.
- **Workflow**: End-to-end media upload and investigation tracking logic.
- **Reports**: Capability to export forensic PDF and CSV reports.
- **Persistence**: SQLite database integration via FastAPI and SQLAlchemy async endpoints.
- **Demo Mode**: Automatic seeding of demo forensic records for immediate testing upon fresh install.
- **UI Enhancements**: Role-based access context and beautifully animated success/error states for investigation saving.

### Fixed
- Addressed database missing greenlet errors on API requests.
- Fixed TypeScript routing bugs on evidence cards.
- Fixed caching persistence on investigation status saves.
