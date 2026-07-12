# Graph Report - reels-saas  (2026-07-12)

## Corpus Check
- 3 files · ~2,340 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 31 nodes · 40 edges · 6 communities (4 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e00c56ee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Reels Studio — SaaS (Telegram Mini App)|Reels Studio — SaaS (Telegram Mini App)]]
- [[_COMMUNITY_reel_engine.py|reel_engine.py]]
- [[_COMMUNITY_generate|generate]]
- [[_COMMUNITY__auth_user|_auth_user]]
- [[_COMMUNITY__rate_ok|_rate_ok]]

## God Nodes (most connected - your core abstractions)
1. `Reels Studio — SaaS (Telegram Mini App)` - 9 edges
2. `main()` - 7 edges
3. `generate()` - 5 edges
4. `make_music()` - 4 edges
5. `_auth_user()` - 3 edges
6. `_rate_ok()` - 3 edges
7. `find_clip()` - 3 edges
8. `ff()` - 3 edges
9. `_run_job()` - 2 edges
10. `phon()` - 2 edges

## Surprising Connections (you probably didn't know these)
- `generate()` --calls--> `_auth_user()`  [EXTRACTED]
  app.py → app.py  _Bridges community 4 → community 3_
- `generate()` --calls--> `_rate_ok()`  [EXTRACTED]
  app.py → app.py  _Bridges community 5 → community 3_

## Import Cycles
- None detected.

## Communities (6 total, 2 thin omitted)

### Community 0 - "Reels Studio — SaaS (Telegram Mini App)"
Cohesion: 0.20
Nodes (9): Reels Studio — SaaS (Telegram Mini App), TODO (дальнейшее продакшен-упрочнение), Безопасность (уже сделано после ревью), Голоса (клоны в ElevenLabs), Деплой на Railway, Как работает, Локальный запуск, Подключить к боту (без кода — через BotFather) (+1 more)

### Community 1 - "reel_engine.py"
Cohesion: 0.38
Nodes (9): api(), download(), dur(), ff(), find_clip(), main(), make_music(), phon() (+1 more)

### Community 3 - "generate"
Cohesion: 0.67
Nodes (3): generate(), _run_job(), Request

## Knowledge Gaps
- **8 isolated node(s):** `Как работает`, `Локальный запуск`, `Деплой на Railway`, `Подключить к боту (без кода — через BotFather)`, `Голоса (клоны в ElevenLabs)` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `generate()` connect `generate` to `app.py`, `_auth_user`, `_rate_ok`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `_auth_user()` connect `_auth_user` to `app.py`, `generate`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **What connects `Как работает`, `Локальный запуск`, `Деплой на Railway` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._