# Project Management - Agent Instructions

## Ticket System Rules
- **Issues**: Problems, bugs, technical debt (issues/{state}/)
- **Features**: New functionality, enhancements (features/{state}/)
- **States**: pending → in-progress → completed/closed
- **File Format**: One ticket = one file, descriptive filename
- **Movement**: Move files between state folders as status changes

## Ticket States
### Issues
- **pending/**: Identified issues awaiting work
- **in-progress/**: Currently being worked on
- **completed/**: Fixed and verified
- **closed/**: Won't fix or no longer relevant

### Features  
- **concept/**: Ideas, not planned for implementation
- **planned/**: Approved for development
- **in-progress/**: Currently being developed
- **completed/**: Implemented and tested

## Ticket Management Process
1. **Create**: New ticket in appropriate pending/ or concept/ folder
2. **Prioritize**: Update priority and assignment in ticket header
3. **Work**: Move to in-progress/ when starting work
4. **Complete**: Move to completed/ when done, update status
5. **Update**: Maintain current state in ticket headers

## Required Ticket Headers
```markdown
**Status**: [Pending/In-Progress/Completed/Closed]
**Priority**: [High/Medium/Low]
**Assigned**: [Session ID or "Unassigned"]
**Estimated Effort**: [Time estimate]
```

## Maintenance Tasks
- Move tickets between folders as status changes
- Update ticket headers with current information
- Reference completed tickets when relevant issues arise
- Keep folder structure organized and consistent

---

> **AI Instructions**: Update ticket states and locations as work progresses. Maintain clear status tracking.