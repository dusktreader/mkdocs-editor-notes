# TODO List

## Table of Contents
1. [Phase 1: Core Parsing](#phase-1-core-parsing)
2. [Phase 2: Note Collection](#phase-2-note-collection)
3. [Phase 3: Aggregator Page](#phase-3-aggregator-page)
4. [Phase 4: Highlighting & Navigation](#phase-4-highlighting--navigation)
5. [Phase 5: Configuration](#phase-5-configuration)
6. [Phase 6: Documentation](#phase-6-documentation)
7. [Phase 7: Testing](#phase-7-testing)

## Phase 1: Core Parsing
- [ ] Create markdown extension class
- [ ] Implement pattern matching for editor note syntax
- [ ] Parse note type and optional label
- [ ] Extract note text/content
- [ ] Store notes with metadata

## Phase 2: Note Collection
- [ ] Implement MkDocs plugin class
- [ ] Hook into page processing events
- [ ] Collect notes from all pages during build
- [ ] Generate unique paragraph/anchor IDs
- [ ] Store page context with each note

## Phase 3: Aggregator Page
- [ ] Create aggregator page generator
- [ ] Group notes by type
- [ ] Format notes with links to source
- [ ] Add page to navigation
- [ ] Handle empty notes case

## Phase 4: Highlighting & Navigation
- [ ] Add anchor IDs to paragraphs containing notes
- [ ] Implement CSS for :target highlighting
- [ ] Test navigation and highlighting
- [ ] Handle edge cases (multiple notes per paragraph)

## Phase 5: Configuration
- [ ] Add configuration schema
- [ ] Implement show/hide markers option
- [ ] Allow custom note types
- [ ] Configure aggregator page location
- [ ] Add enable/disable highlighting option

## Phase 6: Documentation
- [ ] Update quickstart.md with usage examples
- [ ] Update features.md with feature details
- [ ] Update reference.md with API documentation
- [ ] Add editor notes to docs as examples
- [ ] Update index.md with overview

## Phase 7: Testing
- [ ] Write tests for markdown extension
- [ ] Write tests for plugin
- [ ] Write tests for note collection
- [ ] Write tests for aggregator page generation
- [ ] Test highlighting functionality
- [ ] Integration tests
