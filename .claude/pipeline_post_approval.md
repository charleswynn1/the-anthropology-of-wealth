# Post-Approval Pipeline

When the user approves the video (says "render", "publish", "ship it", "looks good", etc.), execute ALL waves below simultaneously where noted. Do not stop between steps. Do not wait for confirmation.

**Multi-project rule:** When completing multiple videos, treat each project independently. As soon as one video's render finishes, immediately proceed with its full post-render pipeline while other renders continue in the background. Each project moves through the pipeline at its own pace.

---

### WAVE 9 — Kick Off (W9a, W9b, W9c all start simultaneously on approval)

**W9a: Render the video** *(the longest track — everything else runs around it)*
```bash
cd /Users/charleswynn/Desktop/The Anthropology of Wealth && npx remotion render CompositionId out/<project>.mp4
```
Verify the output file exists and print its size.

**As soon as W9a finishes → immediately start W10.**

---

**W9b: Upload costs to Google Sheets** *(depends on approval only — costs.json already written during W3a/W3b/W3c)*
```bash
python3 tools/upload_costs.py <project>
```
Reads `projects/<project>/costs.json` and appends a row with the full cost breakdown (Gemini images, ElevenLabs TTS, ElevenLabs music). Does not wait for render.

---

**W9c: Save thumbnail script** *(depends on approval only — W3d already completed during pre-production)*
```bash
cp tools/generate_thumbnail.py projects/<project>/generate_thumbnail.py
```

---

### WAVE 10 — YouTube Upload (depends on W9a)

**W10: Upload to YouTube**

Run the `/youtube-titles` skill against the script's TITLE options and content to generate and select the best title. Use the CORE IDEA and KEY MONEY LESSON as the description. Run:
```bash
python3 tools/youtube_upload.py out/<project>.mp4 \
    --title "<best title from script>" \
    --description "<core idea + key money lesson from script>" \
    --tags "money math,personal finance,financial literacy,investing,budgeting,money tips" \
    --thumbnail projects/<project>/thumbnail-1.png
```
The upload script will:
- Auto-detect scheduling (2-day gap between uploads, or publish immediately if no recent uploads)
- Add the video to the Money Math playlist (auto-creates if needed)
- Upload the primary thumbnail (auto-compresses to JPEG if over 2MB — YouTube API limit)

Print the YouTube URL when complete. Remind the user to add thumbnail-2.png and thumbnail-3.png via YouTube Studio > Test & Compare.

**As soon as W10 finishes → immediately start W11a and W11b simultaneously.**

---

### WAVE 11 — Cleanup (W11a and W11b run in parallel, both depend on W10)

**W11a: Update youtube_titles.md**
Append a row with the date, project slug, chosen title, and YouTube URL.

**W11b: Kill Remotion processes**
```bash
pkill -f remotion || true
pkill -f "node.*remotion" || true
lsof -ti:3000,3100 | xargs kill -9 2>/dev/null || true
```

---

### WAVE 12 — Archive (depends on W11a + W11b + W9c — all three must be done)

**W12: Move project to completed and purge all other project traces**

```bash
rm -f public/<project>/audio public/<project>/images
rmdir public/<project> 2>/dev/null || true
mv projects/<project> projects/completed/<project>
```

Then remove all remaining project traces from every other subdirectory in the repo root:

```bash
# Remove Remotion source files
rm -rf src/<project>
```

Also check and remove any project-named output files:
```bash
rm -f out/<project>.mp4
```

After cleanup, verify:
- `projects/<project>/` — gone (moved to `projects/completed/`)
- `public/<project>/` — gone (symlinks removed)
- `src/<project>/` — gone (Remotion source removed)
- `out/<project>.mp4` — gone (render file removed)
- `projects/completed/<project>/` — exists with all project files intact

The only remaining trace of the project anywhere in the repo is `projects/completed/<project>/`. All project files (script, audio, images, thumbnails, costs.json, generation scripts, topic_research.md) are preserved there.

---

### Post-publish summary
After all waves complete, tell the user:
- Render file path and size
- Production cost total
- YouTube URL
- Whether it was published immediately or scheduled (and when)
- Thumbnail paths for Test & Compare (thumbnail-2.png, thumbnail-3.png)
- Confirmation that project was moved to `projects/completed/`
