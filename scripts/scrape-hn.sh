#!/usr/bin/env bash
# 用 crawl4ai 抓网页并输出 markdown。默认抓 Hacker News 首页。
# 用法: CRAWL4AI_KEY=xxx ./scrape-hn.sh [url]
set -euo pipefail

: "${CRAWL4AI_KEY:?请先设置 CRAWL4AI_KEY 环境变量}"
URL="${1:-https://news.ycombinator.com}"

for cmd in curl jq; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "缺少依赖: $cmd" >&2; exit 1; }
done

curl -s https://api.crawl4ai.com/scrape \
  -H "Authorization: Bearer $CRAWL4AI_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$URL\"}" | jq -r .markdown
