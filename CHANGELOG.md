
# Changelog

All notable changes to ClarityDoc will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- AI-powered chat assistant for document Q&A
- Document summarization (summary, bullets, analysis, Q&A modes)
- Document analysis with custom questions
- AI code generation feature
- AI code review feature
- 10-stage GitLab CI/CD pipeline (dependencies, syntax, services, api, test, quality, package, smoke, release, release_manifest)
- Local GitLab Runner configuration for Windows
- Flask backend with REST API endpoints for AI features
- Frontend JavaScript helpers for AI integration

### Changed
- Migrated environment configuration to `.env` file with `python-dotenv`
- Updated `.gitignore` to exclude virtual environments and build artifacts

### Fixed
- Resolved GitLab Runner shell execution issues on Windows (pwsh/powershell PATH)
- Fixed Python path resolution in CI/CD pipeline for SYSTEM account context
- Fixed `.env` file encoding issues (UTF-8 vs UTF-16)
- Resolved file permission errors in CI/CD build artifacts cleanup

## [0.1.0] - 2026-06-28

### Added
- Initial project structure with Flask backend
- Basic document upload and storage functionality
- Project documentation (README, LICENSE)
