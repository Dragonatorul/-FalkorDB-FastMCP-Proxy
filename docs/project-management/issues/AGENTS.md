# Issues Management - AI Instructions

## Documentation Hierarchy
- **AGENTS.md** (This file): AI-specific issues management process
- **README.md**: Human-readable issues navigation and status
- **State folders**: pending/, in-progress/, completed/, closed/ with issue files

## AI Context for Issues
Issues are problems, bugs, or technical debt organized by current status.
State folders contain issue files that move between folders as status changes.
Each issue file has required headers: Status, Priority, Assigned, Estimated Effort.
Current inventory: 4 pending issues, 0 in other states.

## AI Maintenance Process
1. **Read this AGENTS.md**: Before any issues work
2. **Check current state**: Review file locations and headers
3. **Move files**: Between state folders when status changes
4. **Update headers**: Sync Status field with folder location
5. **Update README.md**: Sync human summary with current state

## Issue State Management (AI Reference)
```
pending/     → in-progress/ → completed/
pending/     → closed/ (won't fix)
```

## Current Issue Inventory
- **pending/**: 4 issues (docker-dual-port, fastmcp-url-tokens, multi-device-testing, complete-tenant-tools)
- **in-progress/**: 0 issues
- **completed/**: 0 issues
- **closed/**: 0 issues

## Required Headers (AI Template)
```markdown
**Status**: [Folder state]
**Priority**: [High/Medium/Low]
**Assigned**: [Session ID or "Unassigned"]
**Estimated Effort**: [Time estimate]
```

---

> **AI Note**: Move issue files between state folders and update headers when status changes.