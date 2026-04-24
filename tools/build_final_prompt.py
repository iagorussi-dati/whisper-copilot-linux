#!/usr/bin/env python3
"""Extract selected approaches from discovery-dati-selecao.md and build final prompt."""
import re

with open("/home/iago/whisper-copilot-lite-linux/prompts/discovery-dati-selecao.md") as f:
    content = f.read()

# Split into header and examples
header_end = content.index("### 1.")
header = content[:header_end]

# Find all situations with their approaches
situations = re.split(r'(#### Situação \d+\.\d+)', content[header_end:])
output = header

for i in range(1, len(situations), 2):
    sit_title = situations[i]  # "#### Situação X.Y"
    sit_body = situations[i+1]
    
    # Check category headers
    cat_match = re.search(r'(### \d+\..+?)(?=\n)', sit_body)
    
    # Find SITUAÇÃO text
    sit_match = re.search(r'(\*\*SITUAÇÃO:\*\*.+?)(?=\n\n\*\*Abordagem)', sit_body, re.DOTALL)
    if not sit_match:
        continue
    sit_text = sit_match.group(1)
    
    # Find selected approach (any X with optional spaces)
    selected = re.search(
        r'(\*\*Abordagem \d+ — Foco:.+?)(?=\*\*Abordagem \d+|\Z)',
        sit_body, re.DOTALL
    )
    
    # Find all approaches and check which is selected
    approaches = list(re.finditer(
        r'(\*\*Abordagem \d+ — Foco:.+?)(?=\*\*Abordagem \d+|$)',
        sit_body, re.DOTALL
    ))
    
    selected_app = None
    for app in approaches:
        app_text = app.group(1)
        if re.search(r'Selecionada:\s*\[.*[Xx].*\]', app_text):
            # Clean: remove Obs and Selecionada lines
            lines = []
            for line in app_text.split('\n'):
                if '✏️ Selecionada' in line:
                    continue
                lines.append(line)
            selected_app = '\n'.join(lines).rstrip()
            break
    
    if selected_app:
        # Check if we need a category header
        before_sit = sit_body[:sit_body.index('**SITUAÇÃO')]
        cat_header = re.search(r'(### \d+\..+)', before_sit)
        if cat_header:
            output += '\n' + cat_header.group(1) + '\n'
        
        output += f'\n{sit_title}\n{sit_text}\n\n{selected_app}\n'

with open("/home/iago/whisper-copilot-lite-linux/prompts/discovery-dati.md", "w") as f:
    f.write(output)

# Count
n_sit = output.count("#### Situação")
n_lines = len(output.split('\n'))
print(f"Final prompt: {n_sit} situations, {n_lines} lines")
