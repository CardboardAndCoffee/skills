#!/usr/bin/env python3
"""Build a self-contained, interactive HTML tutorial from a Markdown walkthrough.

Usage:
    python3 build_tutorial.py <input.md> [output.html]

Reads the Markdown guide and embeds it (verbatim) into a single HTML file that
renders it client-side — no network, no build deps. The HTML is a *view* of the
Markdown (the .md stays canonical), so there's one source of truth for the words
and only the presentation lives here. Re-run after editing the Markdown.

Title, sidebar kicker, the topbar label, and the localStorage progress key are all
derived from the document's first `# H1`, so the same script works for any tutorial.
"""

import difflib
import pathlib
import re
import sys

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def _runtime_slug(text):
    """Mirror the in-page JS slug() so build-time anchor checks match runtime ids."""
    text = re.sub(r"[`*]", "", text.lower())
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    return re.sub(r"\s+", "-", text.strip())

def check_references(md):
    """Scan for broken internal anchor links and structural smells.

    Returns (errors, warnings). Headings/links inside fenced code blocks and inline
    `code` spans are ignored, mirroring what the renderer actually turns into links.
    Anchor matching is case-sensitive because in-browser `getElementById` is too — so
    a link to `#Part-2` against a heading id of `part-2` is correctly flagged dead.
    """
    ids, links, missing_lang = [], [], 0
    in_fence = False
    for lineno, raw in enumerate(md.splitlines(), 1):
        fence = re.match(r"^\s*```(\w*)\s*$", raw)
        if fence:
            if not in_fence and not fence.group(1):
                missing_lang += 1
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", raw)
        if h:
            ids.append(_runtime_slug(h.group(2).strip()))
            continue
        stripped = re.sub(r"`[^`]+`", "", raw)  # inline code is never link text
        for m in re.finditer(r"\]\(#([^)\s]+)\)", stripped):
            links.append((m.group(1), lineno))

    idset = set(ids)
    errors = []
    for target, lineno in links:
        if target not in idset:
            near = difflib.get_close_matches(target, list(idset), n=1, cutoff=0.6)
            hint = f" (did you mean #{near[0]}?)" if near else ""
            errors.append(f"line {lineno}: link to #{target} matches no heading{hint}")

    warnings, counts = [], {}
    for s in ids:
        counts[s] = counts.get(s, 0) + 1
    if "" in counts:
        warnings.append("a heading reduces to an empty anchor id — links to it can't resolve")
    for s, c in counts.items():
        if s and c > 1:
            warnings.append(f"{c} headings share anchor #{s}; links resolve to the first only")
    if missing_lang:
        warnings.append(f"{missing_lang} fenced block(s) have no language tag (house style asks for one)")
    return errors, warnings

def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.exit(__doc__)

    src = pathlib.Path(argv[1]).resolve()
    if not src.exists():
        sys.exit(f"No such file: {src}")
    out = pathlib.Path(argv[2]).resolve() if len(argv) > 2 else src.with_suffix(".html")

    md = src.read_text(encoding="utf-8")

    # The markdown is embedded inside a <script type="text/plain"> block. The HTML
    # parser would end that block early if the text contained "</script". Fail loudly
    # rather than emit a broken file.
    if "</script" in md.lower():
        sys.exit("Refusing to build: markdown contains a literal </script that would break embedding.")

    # Validate references before emitting. Dead internal anchors render as links to
    # nowhere — fail loud rather than ship them; warnings are advisory and still build.
    errors, warnings = check_references(md)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if errors:
        sys.exit("Refusing to build — broken internal links:\n"
                 + "\n".join("  - " + e for e in errors))

    # Derive title / kicker / storage key from the first H1.
    h1_match = re.search(r"^#\s+(.*)$", md, re.MULTILINE)
    h1 = h1_match.group(1).strip() if h1_match else src.stem
    # Short id = the part before the first ":" or em/en dash (e.g. a ticket key like "DEP-12");
    # fallback to the whole title.
    prefix = re.split(r"\s*[:—–-]\s+", h1, maxsplit=1)[0].strip()
    kicker = f"{prefix} · Walkthrough"
    title_tag = f"{h1} · Interactive Walkthrough"
    store_key = f"{slugify(src.stem)}-tutorial-v1"

    html = (TEMPLATE
            .replace("__TITLE_TAG__", esc_html(title_tag))
            .replace("__KICKER__", esc_html(kicker))
            .replace("__DOCTITLE__", esc_html(h1))
            .replace("__TOPBAR__", esc_html(prefix))
            .replace("__STOREKEY__", store_key)
            .replace("__MD__", md))

    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({len(html):,} bytes, {len(md.splitlines())} md lines)")

def esc_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE_TAG__</title>
<style>
  :root{
    --bg:#0f1411; --panel:#161e18; --panel2:#1b241d; --code:#0c120e;
    --text:#dbe4d8; --muted:#8c988a; --faint:#6b756a;
    --accent:#79b765; --accent-d:#5c9a49; --amber:#d8a657; --rule:#27322a;
    --border:#26302a; --shadow:rgba(0,0,0,.35);
    --sidebar:330px;
  }
  html[data-theme="light"]{
    --bg:#f4f6f1; --panel:#ffffff; --panel2:#eef2ea; --code:#f0f3ec;
    --text:#1f2a20; --muted:#5d6b5b; --faint:#869081;
    --accent:#3f8f2c; --accent-d:#357a25; --amber:#9a6a13; --rule:#dde4d8;
    --border:#dce3d6; --shadow:rgba(40,60,40,.10);
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0; background:var(--bg); color:var(--text);
    font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
  }
  a{color:var(--accent); text-decoration:none}
  a:hover{text-decoration:underline}

  /* layout */
  .wrap{display:grid; grid-template-columns:var(--sidebar) 1fr; min-height:100vh}
  .side{
    position:sticky; top:0; height:100vh; overflow-y:auto;
    background:var(--panel); border-right:1px solid var(--border); padding:0;
  }
  .side-head{padding:20px 22px 14px; border-bottom:1px solid var(--border); position:sticky; top:0; background:var(--panel); z-index:2}
  .side-head .kicker{font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); font-weight:700}
  .side-head h1{font-size:18px; margin:6px 0 2px; line-height:1.3}
  .side-head .sub{font-size:12.5px; color:var(--muted)}
  .progress{margin-top:14px}
  .progress .bar{height:8px; border-radius:99px; background:var(--panel2); overflow:hidden; border:1px solid var(--border)}
  .progress .fill{height:100%; width:0; background:linear-gradient(90deg,var(--accent-d),var(--accent)); transition:width .3s ease}
  .progress .lbl{display:flex; justify-content:space-between; font-size:12px; color:var(--muted); margin-top:6px}
  .progress .lbl b{color:var(--text); font-variant-numeric:tabular-nums}

  nav{padding:10px 10px 40px}
  nav .grp{margin:1px 0}
  nav .p-link{
    display:flex; align-items:flex-start; gap:8px; width:100%; text-align:left;
    background:none; border:0; color:var(--text); cursor:pointer;
    font:inherit; font-size:13.5px; font-weight:600; padding:8px 10px; border-radius:8px; line-height:1.35;
  }
  nav .p-link:hover{background:var(--panel2)}
  nav .p-link.active{background:var(--panel2); color:var(--accent)}
  nav .p-link .tw{color:var(--faint); font-size:11px; transition:transform .15s ease; margin-top:2px}
  nav .grp.collapsed .tw{transform:rotate(-90deg)}
  nav .subs{margin:2px 0 6px 0; display:block}
  nav .grp.collapsed .subs{display:none}
  nav .s-link{
    display:block; color:var(--muted); font-size:12.5px; padding:5px 10px 5px 30px;
    border-radius:7px; border-left:2px solid transparent;
  }
  nav .s-link:hover{background:var(--panel2); text-decoration:none; color:var(--text)}
  nav .s-link.active{color:var(--accent); border-left-color:var(--accent); background:var(--panel2)}

  /* content */
  main{max-width:860px; margin:0 auto; padding:46px 40px 120px}
  .doc h1{font-size:30px; line-height:1.2; margin:0 0 6px}
  .doc h2{font-size:23px; margin:52px 0 14px; padding-top:14px; border-top:1px solid var(--rule); scroll-margin-top:20px}
  .doc h2:first-of-type{border-top:0; padding-top:0}
  .doc h3{font-size:17.5px; margin:30px 0 10px; color:var(--text); scroll-margin-top:20px}
  .doc h2 .anchor,.doc h3 .anchor{opacity:0; color:var(--faint); font-weight:400; margin-left:8px; font-size:.7em}
  .doc h2:hover .anchor,.doc h3:hover .anchor{opacity:1}
  .doc p{margin:12px 0}
  .doc strong{color:var(--text); font-weight:700}
  .doc em{color:var(--text)}
  .doc ul,.doc ol{margin:12px 0; padding-left:26px}
  .doc li{margin:6px 0}
  .doc li>ul,.doc li>ol{margin:6px 0}
  hr.part-sep{display:none}

  /* inline code */
  code{
    background:var(--code); border:1px solid var(--border); border-radius:5px;
    padding:.08em .38em; font:13.5px/1.5 "SFMono-Regular",ui-monospace,Menlo,Consolas,monospace;
    color:#cfe6c2;
  }
  html[data-theme="light"] code{color:#2c5e1f}

  /* code blocks */
  .codewrap{position:relative; margin:16px 0}
  .codewrap .lang{
    position:absolute; top:0; left:14px; transform:translateY(-50%);
    font-size:10.5px; letter-spacing:.08em; text-transform:uppercase; font-weight:700;
    color:var(--faint); background:var(--bg); padding:1px 8px; border:1px solid var(--border); border-radius:99px;
  }
  .codewrap pre{
    margin:0; background:var(--code); border:1px solid var(--border); border-radius:10px;
    padding:18px 16px 16px; overflow-x:auto;
  }
  .codewrap pre code{background:none; border:0; padding:0; color:#d4e6c8; font-size:13px; line-height:1.6}
  html[data-theme="light"] .codewrap pre code{color:#243018}
  .copy{
    position:absolute; top:8px; right:8px; z-index:1;
    font:inherit; font-size:11.5px; font-weight:600; cursor:pointer;
    background:var(--panel2); color:var(--muted); border:1px solid var(--border);
    border-radius:7px; padding:4px 9px; opacity:0; transition:opacity .15s ease,color .15s
  }
  .codewrap:hover .copy{opacity:1}
  .copy:hover{color:var(--text)}
  .copy.ok{color:var(--accent); border-color:var(--accent)}

  /* callouts (blockquotes) */
  blockquote{
    margin:16px 0; padding:12px 16px 12px 16px; border-left:3px solid var(--accent);
    background:var(--panel); border-radius:0 10px 10px 0; color:var(--text);
  }
  blockquote.warn{border-left-color:var(--amber); background:linear-gradient(90deg,rgba(216,166,87,.07),transparent)}
  blockquote p{margin:6px 0}
  blockquote p:first-child{margin-top:0}
  blockquote p:last-child{margin-bottom:0}
  blockquote table{font-size:13.5px}

  /* tables */
  .tablewrap{overflow-x:auto; margin:16px 0}
  table{border-collapse:collapse; width:100%; font-size:14px}
  th,td{border:1px solid var(--border); padding:8px 11px; text-align:left; vertical-align:top}
  thead th{background:var(--panel2); color:var(--text); font-weight:700}
  tbody tr:nth-child(even){background:var(--panel)}

  /* task list (acceptance criteria etc.) */
  li.taskitem{list-style:none; margin-left:-22px}
  label.task{display:flex; gap:10px; align-items:flex-start; cursor:pointer}
  label.task input{margin-top:5px; width:16px; height:16px; accent-color:var(--accent); flex:0 0 auto; cursor:pointer}
  li.taskitem.done label.task span{color:var(--muted); text-decoration:line-through; text-decoration-color:var(--faint)}

  /* topbar (mobile) + theme toggle */
  .topbar{display:none}
  .tools{position:fixed; top:14px; right:18px; z-index:30; display:flex; gap:8px}
  .tools button{
    font:inherit; font-size:12.5px; font-weight:600; cursor:pointer; color:var(--muted);
    background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:6px 11px; box-shadow:0 1px 4px var(--shadow)
  }
  .tools button:hover{color:var(--text)}

  .toTop{
    position:fixed; bottom:22px; right:22px; z-index:30; opacity:0; pointer-events:none;
    transition:opacity .2s; background:var(--accent); color:#0c1209; border:0; border-radius:50%;
    width:44px; height:44px; font-size:18px; cursor:pointer; box-shadow:0 4px 14px var(--shadow)
  }
  .toTop.show{opacity:1; pointer-events:auto}

  @media (max-width:900px){
    :root{--sidebar:0px}
    .wrap{grid-template-columns:1fr}
    .side{
      position:fixed; left:0; top:0; width:320px; z-index:40; transform:translateX(-100%);
      transition:transform .25s ease; box-shadow:4px 0 24px var(--shadow);
    }
    body.nav-open .side{transform:translateX(0)}
    body.nav-open .scrim{opacity:1; pointer-events:auto}
    .scrim{position:fixed; inset:0; background:rgba(0,0,0,.5); opacity:0; pointer-events:none; transition:opacity .25s; z-index:35}
    .topbar{
      display:flex; align-items:center; gap:12px; position:sticky; top:0; z-index:20;
      background:var(--panel); border-bottom:1px solid var(--border); padding:10px 14px;
    }
    .topbar .menu{font:inherit; font-weight:700; background:none; border:1px solid var(--border); color:var(--text); border-radius:8px; padding:7px 12px; cursor:pointer}
    .topbar .t{font-size:14px; font-weight:700}
    main{padding:24px 18px 100px}
    .tools{top:9px}
  }
</style>
</head>
<body>
<div class="scrim" id="scrim"></div>
<div class="tools">
  <button id="themeBtn" title="Toggle light / dark">🌙 Theme</button>
  <button id="resetBtn" title="Clear saved progress">↺ Reset</button>
</div>
<button class="toTop" id="toTop" title="Back to top">↑</button>

<div class="wrap">
  <aside class="side" id="side">
    <div class="side-head">
      <div class="kicker">__KICKER__</div>
      <h1 id="docTitle">__DOCTITLE__</h1>
      <div class="sub">Interactive build guide — your progress saves automatically.</div>
      <div class="progress">
        <div class="bar"><div class="fill" id="pfill"></div></div>
        <div class="lbl"><span>Checklist progress</span><span><b id="pdone">0</b> / <b id="ptotal">0</b></span></div>
      </div>
    </div>
    <nav id="nav"></nav>
  </aside>

  <div>
    <div class="topbar">
      <button class="menu" id="menuBtn">☰ Contents</button>
      <span class="t">__TOPBAR__</span>
    </div>
    <main><article class="doc" id="doc"></article></main>
  </div>
</div>

<script type="text/plain" id="md-source">__MD__</script>
<script>
"use strict";

/* ---------------------------------------------------------------------------
   Minimal, purpose-built Markdown -> HTML renderer (offline, no deps).
   Handles the constructs these guides use: headings, hr, fenced code, tables,
   blockquotes (recursively, so callouts can contain tables/lists), ordered &
   unordered lists with nesting + wrapped lines, task lists, and inline
   bold/italic/code/links/autolinks.
--------------------------------------------------------------------------- */
const ESC = s => s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const indentOf = s => (s.match(/^ */)[0]).length;
const isBlockStart = line => {
  const t = line.trim();
  return /^([-*]|\d+\.)\s/.test(t) || t.startsWith(">") || t.startsWith("```")
      || t.startsWith("|") || /^#{1,6}\s/.test(t);
};
function slug(t){
  return t.toLowerCase().replace(/[`*]/g,"").replace(/[^a-z0-9 ]+/g,"")
          .trim().replace(/\s+/g,"-");
}
function inline(text){
  // Pull inline-code spans out first so their contents are never touched by the
  // bold/italic/link passes, then splice them back as <code>.
  // Sentinels use non-printing control chars (written as \x00/\x01) so they can't collide with prose.
  const codes = [];
  text = text.replace(/`([^`]+)`/g, (m,c)=>{ codes.push(c); return "\x00"+(codes.length-1)+"\x01"; });
  text = ESC(text);
  text = text.replace(/&lt;(https?:\/\/[^\s&]+?)&gt;/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
  text = text.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  text = text.replace(/\*\*([^*]+?)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/(^|[^*])\*(?=\S)([^*\n]+?)(?<=\S)\*/g, "$1<em>$2</em>");
  text = text.replace(/\x00(\d+)\x01/g, (m,i)=>"<code>"+ESC(codes[+i])+"</code>");
  return text;
}
function dedent(lines){
  let min = Infinity;
  for(const l of lines){ if(l.trim()!=="") min = Math.min(min, indentOf(l)); }
  if(!isFinite(min)) min = 0;
  return lines.map(l => l.slice(min));
}
function parseList(lines, i){
  const first = lines[i].match(/^(\s*)([-*]|\d+\.)\s+/);
  const baseIndent = first[1].length;
  const ordered = /\d+\./.test(first[2]);
  const startNo = ordered ? parseInt(first[2],10) : 1;
  let out = ordered ? '<ol'+(startNo!==1?' start="'+startNo+'"':'')+'>' : "<ul>";
  while(i < lines.length){
    const line = lines[i];
    if(line.trim()===""){
      let j=i+1; while(j<lines.length && lines[j].trim()==="") j++;
      if(j<lines.length && indentOf(lines[j])===baseIndent && /^(\s*)([-*]|\d+\.)\s+/.test(lines[j])){ i=j; continue; }
      break;
    }
    const m = line.match(/^(\s*)([-*]|\d+\.)\s+(.*)$/);
    if(!m || m[1].length!==baseIndent) break;
    let text = m[3]; i++;
    const child = [];
    while(i<lines.length){
      if(lines[i].trim()===""){
        let j=i+1; while(j<lines.length && lines[j].trim()==="") j++;
        if(j<lines.length && indentOf(lines[j])>baseIndent){ child.push(""); i++; continue; }
        break;
      }
      if(indentOf(lines[i])>baseIndent){ child.push(lines[i]); i++; continue; }
      break;
    }
    let k=0; const lead=[text];
    while(k<child.length && child[k].trim()!=="" && !isBlockStart(child[k])){ lead.push(child[k].trim()); k++; }
    const rest = child.slice(k);
    const itemText = lead.join(" ");
    const task = itemText.match(/^\[([ xX])\]\s+([\s\S]*)$/);
    let inner;
    if(task){
      const ck = task[1].toLowerCase()==="x";
      inner = '<label class="task"><input type="checkbox" data-task'+(ck?" checked":"")+'><span>'+inline(task[2])+"</span></label>";
    } else inner = inline(itemText);
    const body = rest.length ? renderBlocks(dedent(rest)) : "";
    out += "<li"+(task?' class="taskitem"':"")+">"+inner+body+"</li>";
  }
  out += ordered ? "</ol>" : "</ul>";
  return [out, i];
}
function renderBlocks(lines){
  let html="", i=0;
  while(i<lines.length){
    const line = lines[i];
    if(line.trim()===""){ i++; continue; }

    // fenced code
    const fence = line.match(/^\s*```(\w*)\s*$/);
    if(fence){
      const lang = fence[1]||""; const buf=[]; i++;
      while(i<lines.length && !/^\s*```\s*$/.test(lines[i])){ buf.push(lines[i]); i++; }
      i++; // closing fence
      html += '<div class="codewrap">'+(lang?'<span class="lang">'+lang+"</span>":"")
            + '<button class="copy">Copy</button><pre><code>'+ESC(buf.join("\n"))+"</code></pre></div>";
      continue;
    }
    // heading
    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if(h){
      const lvl=h[1].length, txt=h[2].trim(), id=slug(txt);
      html += "<h"+lvl+' id="'+id+'">'+inline(txt)+'<a class="anchor" href="#'+id+'">#</a></h'+lvl+">";
      i++; continue;
    }
    // hr / part separator
    if(/^\s*(---|\*\*\*|___)\s*$/.test(line)){ html += '<hr class="part-sep">'; i++; continue; }

    // blockquote (collect consecutive > lines, render inner recursively)
    if(/^\s*>/.test(line)){
      const buf=[];
      while(i<lines.length && /^\s*>/.test(lines[i])){ buf.push(lines[i].replace(/^\s*>\s?/,"")); i++; }
      const inner = renderBlocks(buf);
      // A callout renders amber when it leads with a warning marker: an emoji, or a
      // bolded lead word, or an admonition tag — plus a keyword fallback.
      const lead = buf.join(" ");
      const warn = /^\s*(⚠️?|🚨|❗)/.test(lead)
                || /^\s*\[!\s*(warn|warning|caution|danger|important)\s*\]/i.test(lead)
                || /<strong>\s*(⚠️?\s*)?(Heads-up|Gotcha|Warning|Caution|Danger|Important|Don't|Never|The #?1|Decision point|Watch out|Pitfall)/i.test(inner)
                || /gotcha|footgun|trips? (up|on)|common mistake/i.test(lead);
      html += '<blockquote'+(warn?' class="warn"':"")+">"+inner+"</blockquote>";
      continue;
    }
    // table
    if(/^\s*\|/.test(line) && i+1<lines.length && /^\s*\|?[\s:|-]+\|/.test(lines[i+1]) && lines[i+1].includes("-")){
      const rows=[];
      while(i<lines.length && /^\s*\|/.test(lines[i])){ rows.push(lines[i]); i++; }
      const cells = r => r.trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(c=>c.trim());
      const head = cells(rows[0]);
      const body = rows.slice(2).map(cells);
      let t='<div class="tablewrap"><table><thead><tr>'+head.map(c=>"<th>"+inline(c)+"</th>").join("")+"</tr></thead><tbody>";
      for(const row of body){ t+="<tr>"+row.map(c=>"<td>"+inline(c)+"</td>").join("")+"</tr>"; }
      t+="</tbody></table></div>";
      html += t; continue;
    }
    // list
    if(/^(\s*)([-*]|\d+\.)\s+/.test(line)){
      const [lh, ni] = parseList(lines, i); html += lh; i = ni; continue;
    }
    // paragraph
    const para=[];
    while(i<lines.length && lines[i].trim()!=="" && !isBlockStart(lines[i]) && !/^(#{1,6})\s/.test(lines[i]) && !/^\s*(---|\*\*\*|___)\s*$/.test(lines[i])){
      para.push(lines[i].trim()); i++;
    }
    if(para.length) html += "<p>"+inline(para.join(" "))+"</p>";
  }
  return html;
}

/* ---------------------------------------------------------------------------
   Render + wire up interactivity
--------------------------------------------------------------------------- */
const STORE_KEY = "__STOREKEY__";
const state = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
state.checks = state.checks || {};

const md = document.getElementById("md-source").textContent;
const doc = document.getElementById("doc");
doc.innerHTML = renderBlocks(md.split("\n"));

// copy buttons
doc.querySelectorAll(".codewrap").forEach(w=>{
  const btn = w.querySelector(".copy"), code = w.querySelector("code");
  btn.addEventListener("click", async ()=>{
    try{ await navigator.clipboard.writeText(code.textContent); }
    catch(e){
      const r=document.createRange(); r.selectNode(code);
      const s=getSelection(); s.removeAllRanges(); s.addRange(r);
      try{ document.execCommand("copy"); }catch(_){} s.removeAllRanges();
    }
    btn.textContent="Copied!"; btn.classList.add("ok");
    setTimeout(()=>{ btn.textContent="Copy"; btn.classList.remove("ok"); }, 1300);
  });
});

// task checkboxes -> progress + persistence
const tasks = [...doc.querySelectorAll("input[data-task]")];
const pdone=document.getElementById("pdone"), ptotal=document.getElementById("ptotal"), pfill=document.getElementById("pfill");
ptotal.textContent = tasks.length;
function refreshProgress(){
  const done = tasks.filter(t=>t.checked).length;
  pdone.textContent = done;
  pfill.style.width = tasks.length ? (100*done/tasks.length)+"%" : "0%";
}
tasks.forEach((t,idx)=>{
  const key="t"+idx;
  if(state.checks[key]) t.checked=true;
  const li=t.closest("li"); if(li) li.classList.toggle("done", t.checked);
  t.addEventListener("change", ()=>{
    state.checks[key]=t.checked; localStorage.setItem(STORE_KEY, JSON.stringify(state));
    if(li) li.classList.toggle("done", t.checked);
    refreshProgress();
  });
});
refreshProgress();

// build sidebar nav from h2 (parts) + h3 (steps)
const nav = document.getElementById("nav");
const heads = [...doc.querySelectorAll("h2, h3")];
let groups=[], cur=null;
heads.forEach(h=>{
  if(h.tagName==="H2"){ cur={h, subs:[]}; groups.push(cur); }
  else if(cur){ cur.subs.push(h); }
});
groups.forEach((g,gi)=>{
  const grp=document.createElement("div"); grp.className="grp";
  const link=document.createElement("button"); link.className="p-link";
  link.innerHTML='<span class="tw">▾</span><span>'+g.h.textContent.replace(/#$/,"").trim()+"</span>";
  link.dataset.target=g.h.id;
  const subsWrap=document.createElement("div"); subsWrap.className="subs";
  g.subs.forEach(s=>{
    const a=document.createElement("a"); a.className="s-link"; a.href="#"+s.id;
    a.textContent=s.textContent.replace(/#$/,"").trim(); a.dataset.id=s.id;
    subsWrap.appendChild(a);
  });
  // clicking the part label scrolls to it; the caret toggles collapse
  link.addEventListener("click",(e)=>{
    if(e.target.classList.contains("tw")){ grp.classList.toggle("collapsed"); return; }
    document.getElementById(g.h.id).scrollIntoView();
    closeNav();
  });
  link.querySelector(".tw").addEventListener("click",(e)=>{ e.stopPropagation(); grp.classList.toggle("collapsed"); });
  subsWrap.querySelectorAll("a").forEach(a=>a.addEventListener("click",closeNav));
  grp.appendChild(link); grp.appendChild(subsWrap); nav.appendChild(grp);
});

// scrollspy
const idToPLink={}, idToSLink={};
groups.forEach(g=>{
  const pl=[...nav.querySelectorAll(".p-link")].find(b=>b.dataset.target===g.h.id);
  idToPLink[g.h.id]=pl;
  g.subs.forEach(s=>{ idToSLink[s.id]=nav.querySelector('.s-link[data-id="'+s.id+'"]'); });
});
let activeId=null;
const spy=new IntersectionObserver((entries)=>{
  entries.forEach(en=>{ if(en.isIntersecting) activeId=en.target.id; });
  if(!activeId) return;
  nav.querySelectorAll(".p-link,.s-link").forEach(el=>el.classList.remove("active"));
  const sl=idToSLink[activeId], pl=idToPLink[activeId];
  if(sl){ sl.classList.add("active");
    const owner=groups.find(g=>g.subs.some(s=>s.id===activeId));
    if(owner && idToPLink[owner.h.id]) idToPLink[owner.h.id].classList.add("active");
  } else if(pl){ pl.classList.add("active"); }
},{rootMargin:"-10% 0px -75% 0px", threshold:0});
heads.forEach(h=>spy.observe(h));

// mobile nav + scrim
const body=document.body, scrim=document.getElementById("scrim");
function closeNav(){ body.classList.remove("nav-open"); }
document.getElementById("menuBtn")?.addEventListener("click",()=>body.classList.toggle("nav-open"));
scrim.addEventListener("click",closeNav);

// theme toggle
const themeBtn=document.getElementById("themeBtn");
function applyTheme(t){
  document.documentElement.dataset.theme=t;
  themeBtn.textContent = t==="dark" ? "☀️ Light" : "🌙 Dark";
}
applyTheme(state.theme || "dark");
themeBtn.addEventListener("click",()=>{
  const next=document.documentElement.dataset.theme==="dark"?"light":"dark";
  state.theme=next; localStorage.setItem(STORE_KEY, JSON.stringify(state)); applyTheme(next);
});

// reset progress
document.getElementById("resetBtn").addEventListener("click",()=>{
  if(!confirm("Clear all checked steps and saved progress on this device?")) return;
  state.checks={}; localStorage.setItem(STORE_KEY, JSON.stringify(state));
  tasks.forEach(t=>{ t.checked=false; const li=t.closest("li"); if(li) li.classList.remove("done"); });
  refreshProgress();
});

// back-to-top
const toTop=document.getElementById("toTop");
addEventListener("scroll",()=>{ toTop.classList.toggle("show", scrollY>700); });
toTop.addEventListener("click",()=>scrollTo({top:0,behavior:"smooth"}));
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main(sys.argv)
