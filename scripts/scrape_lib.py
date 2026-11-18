import sys, re, urllib.request, concurrent.futures as cf
sys.path.insert(0, r"C:/Users/Bully/AppData/Local/Temp/claude/3527d8e23bb102c5/2b97c778-6bde-44c7-9cd6-88d116ece8ad/scratchpad/pylib")
from bs4 import BeautifulSoup

BASE = "https://cekat.ai/en/features/"
CATS = [
 ("Chat", "ai-chatbot whatsapp-chatbot whatsapp-business-api whatsapp-auto-reply instagram-api facebook-messenger-automation embedded-live-chat omnichannel-application whatsapp-multi-agent whatsapp-call-ai-summary visual-chat-flow-builder"),
 ("AI", "multilingual-ai-agent agentic-ai no-code-ai-agent-builder knowledge-base ai-function-calling ai-agent-settings ai-evaluation"),
 ("CRM", "crm-application customer-data-management lead-management pipeline-management complaint-management crm-automation customer-journey-stages ticketing-management-system"),
 ("Marketing", "whatsapp-blast whatsapp-broadcast customer-segmentation automated-follow-up conversion-api-integration marketing-analytics-roas meta-ads-integration tiktok-ads-integration website-tracker utm-generator"),
 ("Order & Automation", "order-automation shipping-cost-automation payment-automation ai-working-hours workflow-automation open-api"),
]
SKIP = re.compile(r"Why|Explore|Results|Security|Frequently|Trusted|Let |Ready", re.I)

def norm(s): return re.sub(r"\s+", " ", s).strip()

def scrape(slug):
    url = BASE + slug
    for attempt in range(4):
        try:
            html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "ignore"); break
        except Exception:
            if attempt == 3: raise
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "nav", "footer", "header"]): t.decompose()
    main = soup.find("main") or soup.body
    title = norm(soup.title.get_text()).split("|")[0].strip() if soup.title else slug
    h1 = norm(main.find("h1").get_text()) if main.find("h1") else ""
    text = norm(main.get_text(" "))
    i = text.find("Start Free Trial")
    m = re.search(r"\d[\d,.]*\+?\s?(businesses|customer)", text[i:]) if i >= 0 else None
    intro = text[i + 16: i + m.start()].strip() if m else ""
    sections = {}
    for h3 in main.find_all("h3"):
        sec = h3.find_parent("section")
        h2 = norm(sec.find("h2").get_text()) if sec and sec.find("h2") else "Details"
        if SKIP.search(h2): continue
        sib = h3.find_next_sibling()
        p = norm(sib.get_text(" ")) if sib else ""
        if not p and h3.parent.find("p"): p = norm(h3.parent.find("p").get_text(" "))
        name = re.sub(r"^0\d\s*", "", norm(h3.get_text()))
        sections.setdefault(h2, []).append((name, p))
    # FAQ
    faqs = []
    for sec in main.find_all("section"):
        h2 = sec.find("h2")
        if h2 and "Frequently" in h2.get_text():
            for q in sec.find_all(["h3", "summary", "button"]):
                qt = norm(q.get_text())
                if qt.endswith("?"):
                    nxt = q.find_next(["p", "div"])
                    faqs.append((qt, norm(nxt.get_text(" ")) if nxt else ""))
    return slug, url, title, h1, intro, sections, faqs

def run():
    slugs = [s for _, g in CATS for s in g.split()]
    with cf.ThreadPoolExecutor(4) as ex:
        return {r[0]: r for r in ex.map(scrape, slugs)}

