# FalkorDB FastMCP Proxy - Issues

This directory contains detailed documentation for current issues and bugs that need to be addressed.

## Issue Categories

### 🔴 High Priority Issues
Critical issues that block core functionality or affect system security.

### 🟡 Medium Priority Issues  
Important issues that impact user experience or system performance.

### 🟢 Low Priority Issues
Minor issues or nice-to-have improvements.

## Current Issues

### High Priority
- **[fastmcp-url-tokens.md](./fastmcp-url-tokens.md)** - FastMCP URL token authentication for opencode compatibility
- **[complete-tenant-tools.md](./complete-tenant-tools.md)** - Complete remaining 3 tenant-aware MCP tools
- **[multi-device-testing.md](./multi-device-testing.md)** - Multi-device testing and validation

### Medium Priority  
- **[docker-dual-port.md](./docker-dual-port.md)** - Docker configuration for dual-port deployment

## Issue Template

When creating new issues, follow this structure:

```markdown
# Issue: [Title]

**Status**: [Pending/In Progress/Completed]  
**Priority**: [High/Medium/Low]  
**Assigned**: [Session/Person]  

## Problem Statement
[Clear description of the issue]

## Technical Details
[Implementation details and constraints]

## Success Criteria
[Measurable criteria for completion]

## Dependencies
[Other issues or features this depends on]

## Estimated Effort
[Time estimate for resolution]
```

## Issue Workflow

1. **Create Issue**: Document the problem and requirements
2. **Prioritize**: Assign priority based on impact and urgency  
3. **Assign**: Allocate to specific session or team member
4. **Track Progress**: Update status as work progresses
5. **Validate**: Test solution against success criteria
6. **Close**: Mark as completed when fully resolved

## Integration with Development

- Each issue should have clear, testable success criteria
- Issues should be small enough to complete in 1-2 sessions
- Cross-references with related code files and documentation
- Link to relevant commits when issues are resolved