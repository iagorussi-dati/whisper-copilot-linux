#!/usr/bin/env python3
"""Parse discovery-dati-selecao.md and generate JSON data for the HTML form."""
import re, json

with open("/home/iago/whisper-copilot-lite-linux/prompts/discovery-dati-selecao.md") as f:
    content = f.read()

situations = []
# Split by #### Situação
parts = re.split(r'#### Situação (\d+\.\d+)', content)
# parts[0] = header, then alternating: id, body
for i in range(1, len(parts), 2):
    sit_id = parts[i]
    body = parts[i+1]
    
    # Extract SITUAÇÃO text
    sit_match = re.search(r'\*\*SITUAÇÃO:\*\*\s*(.+?)(?=\n\n\*\*Abordagem)', body, re.DOTALL)
    sit_text = sit_match.group(1).strip() if sit_match else ""
    
    # Extract approaches
    approaches = []
    app_parts = re.split(r'\*\*Abordagem (\d+) — Foco: (.+?)\*\*', body)
    for j in range(1, len(app_parts), 3):
        app_num = app_parts[j]
        app_focus = app_parts[j+1]
        app_body = app_parts[j+2]
        
        # Extract suggestion lines (💡 ⚠️ 🔴 ✅)
        lines = []
        for line in app_body.split('\n'):
            line = line.strip()
            if line and line[0] in '💡⚠️🔴✅' or (len(line) > 1 and line[:2] in ['💡', '⚠️', '🔴', '✅']):
                lines.append(line)
        
        # Extract obs
        obs_match = re.search(r'> Obs:\s*(.+)', app_body)
        obs = obs_match.group(1).strip() if obs_match else ""
        
        approaches.append({
            "num": int(app_num),
            "focus": app_focus,
            "lines": lines,
            "obs": obs
        })
    
    situations.append({
        "id": sit_id,
        "text": sit_text,
        "approaches": approaches
    })

print(f"Parsed {len(situations)} situations, {sum(len(s['approaches']) for s in situations)} approaches")
with open("/home/iago/whisper-copilot-lite-linux/tools/data.json", "w") as f:
    json.dump(situations, f, ensure_ascii=False, indent=2)
