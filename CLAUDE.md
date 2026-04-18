# Daily AI Model Releases — Routine

Run this routine once per day to compile a briefing and publish it to Discord.
No output files are saved locally.

## Steps

1. **Search** the web using three queries:
   - `new AI model releases <YYYY-MM-DD>`
   - `latest AI model announcements today <YYYY>`
   - `AI launch announcement <Month YYYY>`

2. **Compile** the briefing in this format (in memory — do not save to a file):
   ```
   # AI Model Releases - <Month DD, YYYY>

   ### Top Updates

   - **Model name (Company)** — description. *Status: …*

   ---

   ### Sources

   - [Title](URL)
   ```
   Aim for 5–8 entries. Prioritize LLM/image/video/multimodal launches, major
   version updates, notable benchmarks, open-source releases, and hardware.

3. **Post to Discord** by piping the briefing to the helper script:
   ```bash
   printf '%s' "$BRIEFING" | DISCORD_WEBHOOK_URL="$DISCORD_WEBHOOK_URL" ./post_discord.sh
   ```
   The script splits the content into an embed (title + bullets) and a sources
   message, then POSTs both to the webhook. It exits non-zero on failure.

4. **Commit and push** script changes only (no briefing files) to branch
   `claude/beautiful-cori-8nkvp`:
   ```bash
   git push -u origin claude/beautiful-cori-8nkvp
   ```

## Environment

| Variable              | Description                                  |
|-----------------------|----------------------------------------------|
| `DISCORD_WEBHOOK_URL` | Discord webhook URL for the target channel   |

## Files

| File              | Description                                          |
|-------------------|------------------------------------------------------|
| `post_discord.sh` | Reads briefing from stdin or file, posts to Discord  |
| `CLAUDE.md`       | This routine description                             |
