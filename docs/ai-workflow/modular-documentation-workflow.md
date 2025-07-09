# Modular Documentation Workflow

## Overview

A three-tier documentation hierarchy that serves both AI agents and human users efficiently, preventing context overload while maintaining comprehensive information access.

## The Three-Tier Structure

### Tier 1: Quick Reference Files
**Purpose**: Immediate context and navigation for different audiences

#### AGENTS.md (AI Consumption)
- **Target**: AI agents and LLMs
- **Content**: Compact, descriptive process instructions
- **Size**: 20-40 lines, maximum 100 lines
- **Style**: Information-dense, minimal fluff
- **Focus**: Actionable processes and context for AI decision-making

#### README.md (Human Consumption)  
- **Target**: Human developers and users
- **Content**: Structured summaries and navigation
- **Style**: Well-formatted, readable, concise but complete
- **Focus**: Navigation, quick reference, getting started

### Tier 2: Detailed Documentation
**Purpose**: Comprehensive information for implementation and understanding

- **Target**: Humans needing complete information
- **Content**: Full technical guides, tutorials, specifications
- **Style**: Verbose, well-formatted, human-friendly
- **Focus**: Complete understanding and implementation guidance

### Tier 3: AI Knowledge Base
**Purpose**: AI-specific context optimization

- **Location**: `docs/project-knowledge-base/`
- **Target**: AI agents only (humans redirected to other tiers)
- **Content**: Token-efficient technical context
- **Format**: 10-line summaries + modular detail sections

## Implementation Steps

### 1. Establish Core Structure
```
docs/
├── AGENTS.md (AI navigation)
├── README.md (Human navigation)  
├── [section]/
│   ├── AGENTS.md (AI section process)
│   ├── README.md (Human section navigation)
│   └── [detailed-files].md
└── project-knowledge-base/ (AI only)
    ├── AGENTS.md
    ├── README.md (warning + redirection)
    └── [ai-context-files].md
```

### 2. Create Section AGENTS.md Files
Each section needs an AGENTS.md with:
```markdown
# Section Name - AI Instructions

## Documentation Hierarchy
- AGENTS.md (This file): AI process
- README.md: Human navigation
- Detailed files: Comprehensive content

## AI Context for [Section]
[Brief description of section purpose and content]

## AI Maintenance Process
1. Read this AGENTS.md before work
2. [Section-specific steps]
3. Update README.md after changes

## [Section] Context (AI Reference)
[Key information for AI decision-making]

## AI Update Triggers
[When to update documentation]

## Content Standards (AI Guidelines)
[Formatting and style for target audience]
```

### 3. Implement Core Rules
Add to main AGENTS.md:
```markdown
## Core Rules
- **Section Access Rule**: MUST read section AGENTS.md before working in any docs section
- **Documentation Hierarchy**: AGENTS.md (AI) + README.md (Human) + Detailed content
- **AGENTS.md Size**: Target 50 lines, 100 max - offload context to docs/
```

### 4. Create AI Knowledge Base
- **Warning in README.md**: Clear "AI ONLY" designation
- **10-line summaries**: Essential info in first 10 lines of each file
- **Modular organization**: Separate files for different knowledge domains
- **Token optimization**: Information-dense but readable for LLMs

## Benefits Demonstrated

### Context Management
- **Reduced token usage**: AI reads only needed sections
- **Prevented spam**: Main AGENTS.md stays under 50 lines
- **Modular access**: Specific information when needed

### Human Experience
- **Clear navigation**: README.md files provide logical structure
- **Appropriate depth**: Quick reference vs detailed guides
- **No AI clutter**: Human docs focus on human needs

### AI Efficiency
- **Quick scanning**: 10-line summaries for context determination
- **Process clarity**: Section AGENTS.md provides clear workflows
- **Knowledge preservation**: AI context maintained separately from human docs

## Common Pitfalls

### Anti-Patterns to Avoid
- **Mixing audiences**: Don't put AI instructions in human docs
- **Context bloat**: Keep AGENTS.md files compact
- **Duplicate maintenance**: Use references instead of copying content
- **Missing section files**: Every docs section needs AGENTS.md

### Quality Indicators
- **AGENTS.md under 50 lines**: Good context management
- **Clear section boundaries**: Each area has defined purpose
- **Updated cross-references**: Links remain current
- **Consistent patterns**: Similar structure across sections

## Adaptation for Other Projects

### Technology Stack Considerations
- **Language-specific**: Adapt file formats (.md, .rst, .txt)
- **Tool integration**: Align with existing documentation tools
- **Team size**: Scale section granularity appropriately
- **Project complexity**: Adjust hierarchy depth as needed

### Customization Points
- **Section organization**: Adapt to project structure
- **AI context needs**: Customize knowledge base modules
- **Team workflows**: Align with existing development processes
- **Documentation tools**: Integrate with current toolchain

## Success Metrics

### Quantitative Measures
- **AGENTS.md size**: Target <50 lines, max 100 lines
- **Context efficiency**: Reduced token usage in AI interactions
- **Documentation coverage**: All sections have required files
- **Update frequency**: Regular maintenance of process docs

### Qualitative Indicators
- **AI effectiveness**: Agents can navigate and update docs efficiently
- **Human usability**: Developers find information quickly
- **Maintenance ease**: Documentation stays current with implementation
- **Knowledge transfer**: New team members understand structure

---

> **Implementation Note**: This workflow was developed and refined during the FalkorDB FastMCP Proxy project, achieving 98% completion with comprehensive documentation maintained throughout.