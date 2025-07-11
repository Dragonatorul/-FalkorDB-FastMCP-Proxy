# Documentation Root - AI Instructions

## Documentation Hierarchy
- **AGENTS.md** (This file): AI-specific docs root maintenance process
- **README.md**: Human-readable documentation navigation and structure
- **STATUS.md**: Project status report and completion tracking
- **Subsections**: Each with own AGENTS.md + README.md + detailed content

## AI Context for Docs Root
Main documentation hub with navigation, status tracking, and subsection organization.
Contains project-wide status report and human-readable documentation structure.
Serves as entry point for both human users and AI agents navigating documentation.

## AI Maintenance Process
1. **Read this AGENTS.md**: Before any docs root work
2. **Update STATUS.md**: After major milestones and implementation changes
3. **Sync README.md**: When subsections are added/removed or structure changes
4. **Check subsections**: Ensure all subsections have required AGENTS.md files
5. **Maintain navigation**: Keep cross-references current and accurate

## Docs Root Files (AI Reference)
- **README.md**: Documentation structure, navigation, quick start, guidelines
- **STATUS.md**: Current project status, completion percentage, next steps

## AI Update Triggers
- Major milestone completion (update STATUS.md)
- Documentation structure changes (update README.md)
- New subsection added (ensure AGENTS.md created)
- Project status changes (sync STATUS.md)
- Navigation structure modified (update README.md)

## Content Standards (AI Guidelines)
- **STATUS.md**: Keep current with actual implementation state
- **README.md**: Maintain clear navigation for human users
- **Cross-References**: Ensure all subsection links are accurate
- **Structure**: Follow established 3-tier documentation hierarchy

## Critical Time and Date Management Protocol

**🚨 MANDATORY TIME VERIFICATION 🚨**

**CRITICAL**: Always use system time calls for accurate date/time information.

### System Time Protocol
**MANDATORY**: Before using any date or time information in responses, filenames, or documentation:
1. **Primary**: Use `date -u` command for UTC timestamps
2. **Local time**: Use `date` command when local timezone needed
3. **ISO format**: Use `date -u +"%Y-%m-%d"` for date-only operations
4. **Full timestamp**: Use `date -u +"%Y-%m-%d %H:%M:%S UTC"` for complete timestamps
5. **Verify current date** especially for month-sensitive operations

### Common Error Prevention
- **NEVER ASSUME** the current month/date without checking system time first
- **ALWAYS CALL SYSTEM TIME** before creating timestamped files or documentation
- **MANDATORY VERIFICATION**: Use actual current time from system calls, never environment variables or cached values
- **CRITICAL**: Prevent month confusion (e.g., writing January instead of July)
- **DOUBLE-CHECK**: Always verify the date is correct, especially for month-sensitive operations

**🚨 CRITICAL RULE**: This applies to ALL date/time operations and overrides any cached or assumed date information. Time verification is MANDATORY before any timestamped output.

---

> **AI Note**: Docs root coordinates overall documentation structure and project status tracking.