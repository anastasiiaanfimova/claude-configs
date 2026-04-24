# Resources

Useful repositories and references for Claude Code setup, agents, and tooling.
Worth checking periodically for new patterns and updates.

## Claude Code configuration & agents

### Curated lists
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — most comprehensive index: agents, hooks, CLAUDE.md templates, slash commands, status lines, MCP configs
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — 100+ subagents by task type, with correct YAML frontmatter

### Real setups (copy & adapt)
- [elizabethfuentes12/claude-code-dotfiles](https://github.com/elizabethfuentes12/claude-code-dotfiles) — syncing ~/.claude via Git: what to version, what to exclude (.gitignore patterns)
- [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) — end-to-end example: quality gate hooks, slash commands orchestrating agents, GitHub Actions integration
- [trailofbits/claude-code-config](https://github.com/trailofbits/claude-code-config) — production setup from Trail of Bits security team

### Hooks
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) — hook lifecycle patterns, Python+uv implementation
- [karanb192/claude-code-hooks](https://github.com/karanb192/claude-code-hooks) — copy-paste-ready hook collection
- [nizos/tdd-guard](https://github.com/nizos/tdd-guard) — hooks that block file changes violating TDD principles; good reference for quality gate patterns
- [ldayton/Dippy](https://github.com/ldayton/Dippy) — auto-approve safe bash commands via AST; reduces permission fatigue without disabling safety

### Tooling
- [agent-sh/agnix](https://github.com/agent-sh/agnix) — linter for CLAUDE.md, agents, hooks, skills; IDE plugins included; useful when managing many agents

### Skills & workflows
- [trailofbits/skills](https://github.com/trailofbits/skills) — 15+ security skills: CodeQL, Semgrep, variant analysis, fix verification; good reference for security-auditor agent
- [undeadlist/claude-code-agents](https://github.com/undeadlist/claude-code-agents) — solo dev workflow with multi-auditor patterns, micro-checkpoints, parallel agents

### Reference
- [Anthropic CLAUDE.md](https://github.com/anthropics/claude-code-action/blob/main/CLAUDE.md) — official reference implementation from Anthropic
- [Claude Code hooks docs](https://docs.anthropic.com/en/docs/claude-code/hooks)

## AI ecosystem

### Anthropic official
- [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) — code recipes: prompt caching, vision, tool use; updated with each new API feature
- [Anthropic News](https://www.anthropic.com/news) — model releases, research drops, system cards
- [Claude API Release Notes](https://platform.claude.com/docs/en/release-notes/overview) — API changelogs: new models, limits, pricing

### LLM eval & observability
- [langfuse/langfuse](https://github.com/langfuse/langfuse) — open-source tracing + eval for LLM apps; actively developed, self-hostable alternative to LangSmith
- [Braintrust](https://www.braintrust.dev/) — CI-native eval with regression blocking; relevant when shipping LLM features to prod daily
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) — open-source observability for LLM apps, self-hosted
- [confident-ai/deepeval](https://github.com/confident-ai/deepeval) — pytest-like framework for LLM eval; 50+ metrics (G-Eval, hallucination detection)
- [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) — prompt testing + red-teaming + model comparison; GitHub Actions integration

### Agent engineering & case studies
- [Simon Willison's Weblog](https://simonwillison.net/) — best individual blog on practical AI; near-daily posts with real-world patterns
- [Latent Space](https://www.latent.space/) — newsletter + podcast on AI engineering; interviews with teams shipping agents in prod
- [NirDiamant/agents-towards-production](https://github.com/NirDiamant/agents-towards-production) — end-to-end tutorials: prototype → production, with MLOps and governance

### MCP ecosystem
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) — official reference implementations from Anthropic; source of truth for the spec
- [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — most active curated list, live community

## QA ecosystem

### Blogs & newsletters
- [TestGuild](https://testguild.com) — podcast + blog, practical automation/perf/AI-in-QA content; publishes regularly
- [Ministry of Testing](https://www.ministryoftesting.com) — largest QA community: articles, webinars, conferences
- [Angie Jones](https://angiejones.tech/) — principal engineer at Block, automation strategy
- [Test Automation University](https://testautomationu.applitools.com/) — free courses from practitioners (Angie Jones, Dave Haeffner)

### Testing tools — where to catch updates
- [Playwright releases](https://github.com/microsoft/playwright/releases) — changelog; new features ship frequently
- [mxschmitt/awesome-playwright](https://github.com/mxschmitt/awesome-playwright) — ecosystem of tools around Playwright
- [atinfo/awesome-test-automation](https://github.com/atinfo/awesome-test-automation) — meta-list by language/framework

### Async pipelines & resilience testing
- [kubeshop/tracetest](https://github.com/kubeshop/tracetest) — trace-based tests via OpenTelemetry; assertions on async side effects (queues, webhooks) — fits media-generation pipelines
- [Temporal testing docs](https://docs.temporal.io/develop/typescript/testing-suite) — patterns for testing long-running workflows
- [Gremlin chaos engineering](https://www.gremlin.com/chaos-engineering) — chaos-engineering foundation; relevant when adopting resilience tests for pipelines

### Security QA
- [OWASP API Security Testing Framework](https://owasp.org/www-project-api-security-testing-framework/) — guide to BOLA, broken auth, etc.
- [PortSwigger Web Security Academy](https://portswigger.net/web-security) — free labs from the Burp authors
- [PortSwigger Burp releases](https://portswigger.net/burp/releases) — Burp changelog; new active scans ship regularly
