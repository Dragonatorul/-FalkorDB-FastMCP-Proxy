# Project Management - AI Instructions

## Documentation Hierarchy
- **AGENTS.md** (This file): AI-specific ticket management process
- **README.md**: Human-readable summary and navigation
- **Detailed files**: Comprehensive information for specific features/issues

## Ticket System Process (AI)
- **Issues**: Problems/bugs in `issues/{state}/` folders
- **Features**: New functionality in `features/{state}/` folders  
- **States**: pending → in-progress → completed/closed
- **File Management**: Move files between state folders as status changes
- **Headers Required**: Status, Priority, Assigned, Estimated Effort

## AI Workflow
1. **Read this AGENTS.md**: Before any project-management work
2. **Check current state**: Review ticket locations and headers
3. **Update status**: Move files and update headers when status changes
4. **Maintain structure**: Keep folder organization clean
5. **Update README.md**: Sync human-readable summary after changes

## Ticket States (AI Reference)
```
issues/pending/     → issues/in-progress/ → issues/completed/
issues/pending/     → issues/closed/ (won't fix)
features/concept/   → features/planned/ → features/in-progress/ → features/completed/
```

## Required Headers (AI Template)
```markdown
**Status**: [Current state]
**Priority**: [High/Medium/Low]
**Assigned**: [Session ID or "Unassigned"]
**Estimated Effort**: [Time estimate]
```

## AI Maintenance Tasks
- Move ticket files when status changes
- Update ticket headers with current information
- Sync README.md with current ticket counts and status
- Maintain clean folder structure
- Reference completed tickets for related work

---

> **AI Note**: This file contains AI-specific process information. Humans should refer to README.md for navigation.