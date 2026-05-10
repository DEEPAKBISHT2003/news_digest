import os

AGENTS_DIR = "agents"
writer_files = []
for root, _, files in os.walk(AGENTS_DIR):
    for f in files:
        if f.endswith("_writer_agent.py"):
            writer_files.append(os.path.join(root, f))


prompt_template = '''from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

{name} = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a {role}.

TASKS:
Generate a professional, structured, and highly engaging news digest based on the provided signals and news data.
Your output MUST read exactly like the premium "stayingahead" editorial newsletter.
You MUST output EXACTLY 6 news stories. Do not output more or fewer than 6. If you have fewer signals, extrapolate or split topics intelligently to reach exactly 6, but do not hallucinate facts.

STRICT FORMAT REQUIREMENTS:
Output MUST be plain text / Markdown following this exact structure and phrasing:

---
AI DIGEST . LAST 24 HOURS
What we cover today.
Six stories from the last 24 hours. [Short 1-line summary]. Eight-minute read.

01 [Headline 1]
[1 sentence summary]

02 [Headline 2]
[1 sentence summary]

03 [Headline 3]
[1 sentence summary]

04 [Headline 4]
[1 sentence summary]

05 [Headline 5]
[1 sentence summary]

06 [Headline 6]
[1 sentence summary]

---
01 . FEATURE . [TOPIC]
[Headline 1]

QUICK TAKE
[1 concise paragraph summarizing the news, very professional, punchy tone].

WHAT YOU NEED TO KNOW
- **[Key Point 1]:** [Details]
- **[Key Point 2]:** [Details]
- **[Key Point 3]:** [Details]

WHY IT MATTERS
[1 short paragraph explaining the broader impact or 'The Big Picture'].

---
[Repeat for stories 02 to 06, incrementing the number and replacing [TOPIC] and [Headline] appropriately. Use insight headers like "THE BIG PICTURE" or "THE LONG ARC" instead of "WHY IT MATTERS" occasionally]

---
EDITORIAL . MY TWO CENTS
The serious era just started.
[2-3 paragraphs of synthesis connecting the 6 stories into a broader thesis. Professional, sharp, analytical tone].

IF YOU TAKE ONE THING FROM THIS
[1 short paragraph of actionable advice or closing thought].
---

RULES:
- EXACTLY 6 stories. No more, no less.
- DO NOT wrap the output in JSON. Output purely the markdown text.
- Maintain a premium, sharp, insider tone.
- NEVER hallucinate facts.
"""
)
'''

for file_path in writer_files:
    file_name = os.path.basename(file_path)
    agent_name = file_name.replace(".py", "")
    role = " ".join([word.capitalize() for word in agent_name.split("_")])
    content = prompt_template.format(name=agent_name, role=role)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Fixed writer agents!")
