# Ticket Management Workflow

## Overview

A state-based ticket management system where issues and features are organized into folders representing their current status, with AI agents responsible for moving files between states and maintaining organization.

## State-Based Organization

### Issues (Problems/Bugs)
```
issues/
├── pending/        # Identified issues awaiting work
├── in-progress/    # Currently being worked on
├── completed/      # Fixed and verified
└── closed/         # Won't fix or no longer relevant
```

### Features (New Functionality)
```
features/
├── concept/        # Ideas, not planned for implementation
├── planned/        # Approved for development
├── in-progress/    # Currently being developed
└── completed/      # Implemented and tested
```

## File-Based Ticket System

### One Ticket = One File
- **Descriptive filenames**: `ISSUE-docker-dual-port.md`, `collaborative-queries.md`
- **Complete ticket info**: All details in single markdown file
- **Physical location**: File location indicates current status
- **Move between folders**: Status changes trigger file movement

### Required Headers
Each ticket file must include:
```markdown
**Status**: [Current folder state]
**Priority**: [High/Medium/Low]
**Assigned**: [Session ID or "Unassigned"]
**Estimated Effort**: [Time estimate]
```

## AI Workflow Process

### 1. State Assessment
Before any ticket work:
```markdown
1. Read section AGENTS.md (docs/project-management/[issues|features]/AGENTS.md)
2. Check current file locations in state folders
3. Review ticket headers for status consistency
4. Identify tickets needing status updates
```

### 2. Status Updates
When ticket status changes:
```bash
# Move file between folders
mv source_folder/ticket.md target_folder/ticket.md

# Update Status header in file
**Status**: [New status matching folder]

# Update assignment if starting work
**Assigned**: [Session ID]
```

### 3. Inventory Maintenance
After any ticket changes:
```markdown
1. Update README.md with current counts
2. Verify folder organization is clean
3. Check header consistency across tickets
4. Update human-readable summaries
```

## State Transition Rules

### Issue Lifecycle
- **pending** → **in-progress**: When starting work on issue
- **in-progress** → **completed**: When issue is fixed and verified
- **in-progress** → **pending**: If work is paused/reassigned
- **pending** → **closed**: If won't fix or no longer relevant

### Feature Lifecycle  
- **concept** → **planned**: When feature is approved for development
- **planned** → **in-progress**: When development begins
- **in-progress** → **completed**: When feature is implemented and tested
- **in-progress** → **planned**: If development is paused

## AI Automation Capabilities

### Automatic Maintenance
AI agents can automatically:
- **Move ticket files** between state folders when status changes
- **Update headers** to match current folder location
- **Sync README.md** with current ticket counts and status
- **Maintain organization** by keeping folders clean and consistent

### Status Tracking
AI maintains awareness of:
- **Current inventory**: Count of tickets in each state
- **Work assignment**: Which tickets are assigned to current session
- **Priority distribution**: High/Medium/Low priority breakdown
- **Effort estimates**: Time tracking for project planning

## Implementation Benefits

### Visual Organization
- **Folder structure** immediately shows project status
- **File location** indicates current state without opening file
- **Clean separation** between different types of work
- **Easy navigation** for both AI and human users

### Process Efficiency
- **Atomic operations**: Move file = update status
- **Consistent tracking**: Headers always match folder location
- **Automated maintenance**: AI handles routine organization tasks
- **Clear workflows**: Defined processes for state transitions

## Setup Instructions

### 1. Create Folder Structure
```bash
mkdir -p docs/project-management/{issues,features}/{pending,in-progress,completed}
mkdir -p docs/project-management/issues/closed
mkdir -p docs/project-management/features/{concept,planned}
```

### 2. Create Section AGENTS.md Files
- **issues/AGENTS.md**: AI process for issue management
- **features/AGENTS.md**: AI process for feature management
- Include state management workflows and header requirements

### 3. Establish Header Standards
Create templates for:
- **Issue template**: Status, Priority, Assigned, Estimated Effort
- **Feature template**: Status, Priority, Category, Estimated Effort

### 4. Train AI Workflow
Add to main AGENTS.md:
```markdown
- **Tickets**: Maintain features/issues in docs/project-management/ using state folders
```

## Common Operations

### Creating New Tickets
```markdown
1. Create file in appropriate initial state folder (pending/ or concept/)
2. Include all required headers
3. Write clear problem statement or feature description
4. Update README.md with new ticket count
```

### Moving Tickets
```markdown
1. Identify status change need
2. Move file to appropriate target folder
3. Update Status header to match new folder
4. Update Assigned field if taking ownership
5. Update README.md inventory
```

### Completing Work
```markdown
1. Verify work completion meets acceptance criteria
2. Move file to completed/ folder
3. Update Status header to "Completed"
4. Document completion details in ticket
5. Update README.md counts
```

## Adaptation Guidelines

### Project Customization
- **State names**: Adapt folder names to team workflow (e.g., "review", "testing")
- **Header fields**: Add project-specific metadata requirements
- **File naming**: Establish conventions appropriate to project type
- **Workflow rules**: Customize transition rules for team process

### Integration Options
- **Git integration**: Use branch names or commit messages to trigger status updates
- **Tool integration**: Connect with existing project management tools
- **Automation triggers**: Set up automated status updates based on code changes
- **Reporting**: Generate status reports from folder organization

## Success Metrics

### Organization Quality
- **Folder consistency**: Files in correct folders for their status
- **Header accuracy**: Status headers match folder locations
- **Clean structure**: No orphaned or misplaced files
- **Up-to-date counts**: README.md reflects actual inventory

### Process Efficiency
- **Fast status updates**: Quick file moves for status changes
- **Clear visibility**: Project status obvious from folder structure
- **Reduced overhead**: Minimal maintenance required
- **AI autonomy**: AI can manage routine ticket organization

---

> **Real-World Results**: This system successfully managed 4 pending issues and multiple features throughout the FalkorDB FastMCP Proxy development, with AI agents maintaining organization automatically.