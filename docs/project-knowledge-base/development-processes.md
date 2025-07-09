# Development Processes - AI Reference

## Summary (Lines 1-10)
Complete development workflow processes for FalkorDB FastMCP Proxy project.
Covers: git workflow, commit standards, testing procedures, deployment steps.
Key processes: semantic versioning, atomic commits, documentation updates, status tracking.
Critical rules: NEVER commit without user request, read section AGENTS.md first.
Status: 98% complete, ready for initial deployment.
Main workflow: develop → test → document → commit → deploy.
Authentication: OAuth 2.1 Bearer tokens, RSA JWT validation.
Stack: FastMCP proxy (3001) → MCPServer v1.1.0 (3000) → FalkorDB (6379).
Next: First deployment and Claude Desktop integration testing.

## Git Workflow
- **Branch**: feat/fastmcp-proxy-integration (current working branch)
- **Commit Format**: `<type>(<scope>): <description>` + opencode footer
- **Types**: feat, fix, docs, style, refactor, test, build, ci, chore
- **Atomic Commits**: One logical change per commit
- **Never Commit**: Without explicit user request

## Documentation Process
1. Read section AGENTS.md before working in any docs section
2. Update AGENTS.md (AI), README.md (Human), detailed content (tier structure)
3. AI knowledge → docs/project-knowledge-base/
4. Status updates → docs/STATUS.md after major milestones
5. Ticket management → move files between state folders

## Testing Workflow
- **Integration**: `python tests/test_remote_mcp.py`
- **Stack Health**: `docker-compose ps` then logs review
- **Token Generation**: `python src/fastmcp_proxy.py`
- **Claude Desktop**: Manual integration testing with generated token

## Deployment Process
1. Start stack: `docker-compose up -d`
2. Verify services: `docker-compose ps`
3. Test integration: `python tests/test_remote_mcp.py`
4. Generate token: `python src/fastmcp_proxy.py`
5. Configure Claude Desktop with token
6. Validate 4 MCP tools functionality

## Status Tracking
- Update docs/STATUS.md after major milestones
- Move tickets between state folders as work progresses
- Maintain implementation percentage in status reports
- Document blockers and next steps clearly

## Code Standards
- Python: 4 spaces, snake_case, minimal comments
- Error handling: Comprehensive with structured responses
- Security: No credential logging, secure header forwarding
- Type hints: Where possible, self-documenting code preferred