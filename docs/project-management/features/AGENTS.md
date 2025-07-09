# Features Management - AI Instructions

## Documentation Hierarchy
- **AGENTS.md** (This file): AI-specific features management process
- **README.md**: Human-readable features navigation and status
- **State folders**: concept/, planned/, in-progress/, completed/ with feature files

## AI Context for Features
Features are new functionality or enhancements organized by development status.
State folders contain feature files that move between folders as development progresses.
Each feature file has required headers: Status, Priority, Category, Estimated Effort.
Current inventory: 3 concept features, 1 completed feature, 0 in other states.

## AI Maintenance Process
1. **Read this AGENTS.md**: Before any features work
2. **Check current state**: Review file locations and headers
3. **Move files**: Between state folders when status changes
4. **Update headers**: Sync Status field with folder location
5. **Update README.md**: Sync human summary with current state

## Feature State Management (AI Reference)
```
concept/ → planned/ → in-progress/ → completed/
```

## Current Feature Inventory
- **concept/**: 3 features (collaborative-queries, graphql-query-builder, web-ui-user-management)
- **planned/**: 0 features
- **in-progress/**: 0 features  
- **completed/**: 1 feature (cicd-pipeline-docker-semver)

## Required Headers (AI Template)
```markdown
**Status**: [Folder state]
**Priority**: [High/Medium/Low/Not Applicable]
**Category**: [Core/Enhancement/Enterprise/Integration]
**Estimated Effort**: [Time estimate]
```

---

> **AI Note**: Move feature files between state folders and update headers when development status changes.