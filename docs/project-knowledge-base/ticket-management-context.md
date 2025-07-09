# Ticket Management Context - AI Reference

## Summary (Lines 1-10)
Ticket lifecycle and state management for features and issues in project-management section.
Structure: features/{concept,planned,in-progress,completed}, issues/{pending,in-progress,completed,closed}.
Process: Create in initial state → move files between folders as status changes.
Headers required: Status, Priority, Assigned, Estimated Effort in each ticket file.
Current state: 4 pending issues, 3 concept features, 1 completed feature.
AI workflow: Read section AGENTS.md → check current state → update/move → sync README.md.
File naming: Descriptive names, one ticket per file, move entire file between folders.
Status tracking: Physical file location indicates current status, headers confirm.
Maintenance: Keep folder organization clean, update human README.md after changes.

## Ticket State Folders
### Issues (Problems/Bugs)
```
issues/
├── pending/        # 4 files: ISSUE-docker-dual-port.md, etc.
├── in-progress/    # 0 files currently
├── completed/      # 0 files currently  
└── closed/         # 0 files currently (won't fix)
```

### Features (New Functionality)
```
features/
├── concept/        # 3 files: collaborative-queries.md, etc.
├── planned/        # 0 files currently
├── in-progress/    # 0 files currently
└── completed/      # 1 file: cicd-pipeline-docker-semver.md
```

## Required Ticket Headers
```markdown
**Status**: [Current folder state]
**Priority**: [High/Medium/Low]
**Assigned**: [Session ID or "Unassigned"]  
**Estimated Effort**: [Time estimate]
```

## AI Workflow for Ticket Management
1. **Read AGENTS.md**: Always read docs/project-management/AGENTS.md first
2. **Assess Current State**: Check file locations and headers
3. **Update Status**: Move files between folders when status changes
4. **Update Headers**: Sync Status field with folder location
5. **Sync README.md**: Update human-readable summary with current counts

## Current Ticket Inventory
### Pending Issues (4)
- ISSUE-docker-dual-port.md (Medium priority)
- ISSUE-fastmcp-url-tokens.md (High priority) 
- ISSUE-multi-device-testing.md (High priority)
- ISSUE-complete-tenant-tools.md (High priority)

### Concept Features (3) 
- collaborative-queries.md (Not planned)
- graphql-query-builder.md (Not planned)
- web-ui-user-management.md (Not planned)

### Completed Features (1)
- cicd-pipeline-docker-semver.md (Implemented)

## File Movement Process
### When Status Changes
1. **Move File**: `mv source_folder/ticket.md target_folder/ticket.md`
2. **Update Header**: Change Status field to match new folder
3. **Update Assigned**: Set to current session ID when starting work
4. **Update README**: Sync folder counts in human documentation

### State Transitions
- **Issues**: pending → in-progress → completed/closed
- **Features**: concept → planned → in-progress → completed

## Maintenance Rules
- **One File = One Ticket**: No combining multiple issues/features
- **Descriptive Names**: File names should clearly indicate the ticket content
- **Clean Organization**: No orphaned files, consistent folder structure
- **Header Accuracy**: Status field must match folder location
- **Human Sync**: Update README.md after any organizational changes