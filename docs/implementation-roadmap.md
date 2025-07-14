# FalkorDB FastMCP Proxy - Implementation Roadmap

## Overview

This document outlines a three-phase approach to evolve the FalkorDB FastMCP Proxy from its current authentication-focused implementation to a comprehensive client interface with protocol conversion, authentication handling, and user management capabilities.

## Current State

- ✅ Local client solution for Claude Desktop (DXT) and opencode
- ✅ Bearer token authentication in proxy
- ❌ Duplicated authentication logic between proxy and backend
- ❌ No protocol-level authentication format conversion
- ❌ No user management capabilities

## Target Architecture

```
Clients → FastMCP Proxy (Protocol + Auth Format + User Mgmt) → FalkorDB-MCPServer (Business Logic)
```

---

## Phase 1: Pass-Through Proxy (Protocol Conversion Focus)

**Goal**: Convert proxy to pure protocol converter, move all authentication to backend

### 1.1 Remove Proxy Authentication
- [ ] Remove `BearerAuthProvider` from FastMCP proxy
- [ ] Remove all JWT validation logic from proxy
- [ ] Configure proxy as pure protocol converter
- [ ] Update proxy to forward all headers transparently

### 1.2 Configure Backend Authentication
- [ ] Deploy FalkorDB-MCPServer fork with multi-tenant support
- [ ] Configure backend environment variables:
  ```env
  ENABLE_MULTI_TENANCY=true
  MULTI_TENANT_AUTH_MODE=bearer
  BEARER_JWKS_URI=https://auth-provider/.well-known/jwks.json
  BEARER_ISSUER=https://auth-provider
  BEARER_AUDIENCE=falkordb-proxy
  TENANT_GRAPH_PREFIX=true
  ```

### 1.3 Update Client Configurations
- [ ] Update Claude Desktop DXT to pass Bearer tokens directly
- [ ] Update opencode configuration to use backend authentication
- [ ] Test end-to-end authentication flow

### 1.4 Validation
- [ ] Verify proxy forwards Authorization headers correctly
- [ ] Confirm backend handles all authentication and tenant isolation
- [ ] Test both Claude Desktop and opencode clients
- [ ] Validate no authentication logic remains in proxy

**Deliverables**:
- Pure protocol conversion proxy
- Backend-only authentication
- Updated client configurations
- Working end-to-end flow

---

## Phase 2: Authentication Format Conversion

**Goal**: Add protocol-level authentication format conversion while maintaining backend auth

### 2.1 Query Parameter Authentication Support
- [ ] Implement middleware to detect `?auth=TOKEN` query parameters
- [ ] Convert query parameter to `Authorization: Bearer TOKEN` header
- [ ] Strip auth parameter from forwarded requests
- [ ] Maintain backward compatibility with existing header auth

### 2.2 Multiple Auth Format Support
- [ ] Support `?token=JWT` parameter (opencode compatibility)
- [ ] Support `?auth=JWT` parameter (web client compatibility)
- [ ] Support standard `Authorization: Bearer JWT` header
- [ ] Implement format detection and normalization

### 2.3 Enhanced Client Support
- [ ] Update opencode configuration to use query parameter auth
- [ ] Create web client examples using query parameter auth
- [ ] Maintain Claude Desktop header-based auth
- [ ] Document all supported authentication formats

### 2.4 Testing and Validation
- [ ] Test all authentication formats
- [ ] Verify backend receives normalized Bearer headers
- [ ] Validate tenant isolation works across all auth formats
- [ ] Performance testing with different auth methods

**Deliverables**:
- Multi-format authentication support
- Query parameter to header conversion
- Enhanced client compatibility
- Comprehensive auth format documentation

---

## Phase 3: User Management System

**Goal**: Add comprehensive user and tenant management capabilities

### 3.1 User Management API
- [ ] Design user management data model
- [ ] Implement user CRUD operations:
  - `POST /api/users` - Create user
  - `GET /api/users` - List users
  - `GET /api/users/{id}` - Get user details
  - `PUT /api/users/{id}` - Update user
  - `DELETE /api/users/{id}` - Delete user

### 3.2 Token Management System
- [ ] Implement JWT token generation endpoints:
  - `POST /api/tokens` - Generate new token
  - `GET /api/tokens` - List user tokens
  - `DELETE /api/tokens/{id}` - Revoke token
- [ ] Token expiration and renewal logic
- [ ] Token scope and permission management

### 3.3 Tenant Management
- [ ] Tenant creation and management:
  - `POST /api/tenants` - Create tenant
  - `GET /api/tenants` - List tenants
  - `PUT /api/tenants/{id}` - Update tenant
- [ ] User-tenant association management
- [ ] Tenant-specific configuration options

### 3.4 Web Administration Interface
- [ ] Create React/Vue.js admin dashboard
- [ ] User management interface:
  - User creation/editing forms
  - Token generation interface
  - User activity monitoring
- [ ] Tenant management interface:
  - Tenant creation/configuration
  - User assignment to tenants
  - Tenant usage analytics

### 3.5 Security and Permissions
- [ ] Admin authentication system
- [ ] Role-based access control (RBAC)
- [ ] Audit logging for user management operations
- [ ] Rate limiting for token generation

### 3.6 Integration and Documentation
- [ ] API documentation with OpenAPI/Swagger
- [ ] User management CLI tools
- [ ] Integration examples for common auth providers
- [ ] Migration tools for existing users

**Deliverables**:
- Complete user management API
- Web administration interface
- Token lifecycle management
- Tenant management system
- Security and audit capabilities

---

## Implementation Timeline

### Phase 1: 1-2 weeks
- **Week 1**: Remove proxy auth, configure backend
- **Week 2**: Update clients, testing, validation

### Phase 2: 2-3 weeks  
- **Week 1**: Query parameter auth conversion
- **Week 2**: Multiple format support, client updates
- **Week 3**: Testing, documentation

### Phase 3: 4-6 weeks
- **Week 1-2**: User management API and data model
- **Week 3-4**: Web interface development
- **Week 5**: Security, permissions, audit logging
- **Week 6**: Documentation, testing, deployment

## Success Criteria

### Phase 1 Success
- [ ] Zero authentication logic in proxy
- [ ] All authentication handled by backend
- [ ] Both client types working correctly
- [ ] Clean separation of concerns

### Phase 2 Success
- [ ] Multiple authentication formats supported
- [ ] Seamless format conversion
- [ ] Enhanced client compatibility
- [ ] Maintained security posture

### Phase 3 Success
- [ ] Complete user lifecycle management
- [ ] Self-service token generation
- [ ] Multi-tenant administration
- [ ] Production-ready security features

## Risk Mitigation

### Technical Risks
- **Authentication bypass**: Comprehensive testing of all auth paths
- **Token security**: Proper JWT validation and secure token storage
- **Performance impact**: Load testing with auth conversion overhead

### Operational Risks
- **Migration complexity**: Phased rollout with backward compatibility
- **User disruption**: Maintain existing client configurations during transitions
- **Security vulnerabilities**: Security review at each phase completion

## Dependencies

### External Dependencies
- FalkorDB-MCPServer fork deployment
- JWKS endpoint for token validation
- Database for user management (PostgreSQL/SQLite)

### Internal Dependencies
- FastMCP library compatibility
- Client configuration updates
- Documentation updates

---

## Conclusion

This three-phase approach provides a clear path from the current authentication-focused proxy to a comprehensive client interface system. Each phase builds upon the previous one while maintaining backward compatibility and operational stability.

The final result will be a robust, scalable system that serves as the complete client-facing interface for FalkorDB access, with clean separation between protocol concerns (proxy) and business logic (backend).