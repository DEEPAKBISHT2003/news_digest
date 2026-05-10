from utils.pdf_export import export_digest_to_pdf

test_text = """---
AI DIGEST . LAST 24 HOURS
What we cover today.
Six stories from the last 24 hours. Wall Street, robotics labs, and an emotion paper. Eight-minute read.

01 Claude just took over Wall Street
10 finance agent templates, Microsoft 365 add-ins, Moody's data inside Claude.

02 Anthropic just locked in Goldman
$1.5B joint venture to embed Claude across mid-market firms.

03 AI is about to leave the cloud behind
Neuromorphic chips. Sub-watt always-on inference.

04 Claude has 171 emotion vectors
Anthropic interpretability paper. Boost the "desperate" vector.

05 The US just put every frontier lab on a leash
Google, Microsoft, xAI signed pre-deployment testing pacts.

06 AI agents just became your org chart
Cofounder 2 shipped. Engineering, sales, marketing.

---
01 . FEATURE . WALL STREET
Claude just took over Wall Street

QUICK TAKE
Anthropic released 10 ready-to-run AI agent templates for financial services on Tuesday at an invite-only event in New York.

WHAT YOU NEED TO KNOW
- **The 10 templates:** Pitch builder, Meeting preparer, Earnings reviewer, Model builder.
- **The Microsoft 365 layer:** Claude is now inside Excel, PowerPoint, Word.
- **The market reaction:** FactSet fell 8.1%.

WHY IT MATTERS
Anthropic said financial institutions make up 40% of its top 50 customers. This launch is not Anthropic asking permission.

---
02 . INVESTMENT . DISTRIBUTION
Anthropic just locked in Goldman

QUICK TAKE
The day before the Wall Street agent launch, Anthropic disclosed a $1.5 billion joint venture with Blackstone, Hellman & Friedman, and Goldman Sachs.

WHAT YOU NEED TO KNOW
- **The structure:** approximately $1.5B total.
- **The vehicle's job:** a forward-deployed engineering operation.
- **The competitive note:** Bloomberg reports OpenAI is building a comparable JV structure.

THE BIG PICTURE
Software vendors usually fight for distribution. Anthropic just bought it.

---
EDITORIAL . MY TWO CENTS
The serious era just started.

The model layer was the conversation for two years. The conversation just moved. It moved to distribution, deployment, oversight, internal state monitoring.
Anthropic understands this. Claude inside Excel is a deeper hook than any benchmark.

IF YOU TAKE ONE THING FROM THIS
For the next 18 months, the AI question that matters is not "which model is best." It is "where is your model embedded."
---
"""

if __name__ == "__main__":
    path = export_digest_to_pdf(test_text, output_dir="output")
    print(f"PDF successfully generated at: {path}")
