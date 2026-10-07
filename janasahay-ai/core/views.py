"""JANASAHAY AI - page views."""
import hmac

import pandas as pd
import streamlit as st

from core import rag, ui

STATES = ["All India", "Andhra Pradesh", "Karnataka", "Kerala", "Maharashtra", "Tamil Nadu", "Telangana",
          "Uttar Pradesh", "West Bengal", "Gujarat", "Rajasthan", "Bihar", "Delhi", "Other"]
SUGGEST = ["What scholarships are available for students?", "What documents are required for farmer schemes?",
           "Am I eligible for any government scheme?", "How can I apply for a women entrepreneur scheme?"]


def goto(page: str):
    st.session_state.nav = page


def no_docs() -> bool:
    if rag.registry():
        return False
    st.info("📭 The knowledge base is empty. Upload documents (admin) or load the built-in sample scheme documents to try the app.")
    if st.button("📥 Load sample scheme documents", key="samples_" + st.session_state.get("nav", "")):
        with st.spinner("Indexing sample documents..."):
            try:
                n = rag.load_samples()
                st.success(f"Indexed {n} sample documents.")
                st.rerun()
            except rag.RagError as err:
                st.error(str(err))
    return True


def require_admin() -> bool:
    pw = rag.get_secret("ADMIN_PASSWORD")
    if not pw:
        st.warning("🔒 Admin features are disabled because ADMIN_PASSWORD is not configured. Set it in Streamlit secrets or the environment.")
        return False
    if st.session_state.get("admin"):
        return True
    st.markdown("#### 🔒 Admin login")
    with st.form("admin_login"):
        p = st.text_input("Admin password", type="password")
        if st.form_submit_button("Unlock", type="primary"):
            if hmac.compare_digest(p.encode(), pw.encode()):
                st.session_state.admin = True
                st.rerun()
            st.error("Incorrect password.")
    return False


# ---------------------------------------------------------------- Home
def home():
    ui.hero()
    st.button("🤖 Ask JANASAHAY AI", type="primary", on_click=goto, args=("🤖 AI Assistant",), use_container_width=True)
    st.write("")
    feats = [("🤖", "AI Scheme Assistant", "Ask questions about government schemes using natural language.", "🤖 AI Assistant"),
             ("🎯", "Eligibility Checker", "Find schemes that may match your age, occupation, education and income.", "🎯 Eligibility Checker"),
             ("🔎", "Smart Scheme Search", "Search government scheme documents using semantic AI retrieval.", "🔎 Search Schemes")]
    for col, (i, t, d, p) in zip(st.columns(3), feats):
        with col:
            ui.card(i, t, d)
            st.button("Open →", key="f_" + t, on_click=goto, args=(p,))
    st.write("")
    s = rag.stats()
    for col, (l, v) in zip(st.columns(4), [("Government Documents", s["docs"]), ("Indexed Knowledge Chunks", s["chunks"]),
                                           ("Schemes Available", s["schemes"]), ("AI Queries", s["queries"])]):
        with col:
            ui.stat(l, v)
    st.markdown("### How It Works")
    steps = ["Upload / collect official documents", "AI processes the documents", "RAG retrieves relevant information",
             "Gemini generates a grounded answer", "Sources are displayed"]
    for col, (i, t) in zip(st.columns(5), enumerate(steps, 1)):
        with col:
            ui.step(i, t)
    st.write("")
    no_docs()


# ---------------------------------------------------------------- Assistant
def _render(m):
    st.markdown(m["content"])
    ui.sources(m.get("sources", []))


def assistant():
    ui.header("Ask JANASAHAY AI", "Get answers from verified government scheme documents.")
    msgs = st.session_state.setdefault("chat", [])
    if no_docs():
        return
    c1, c2 = st.columns([5, 1])
    c2.button("🗑 Clear chat", on_click=lambda: st.session_state.update(chat=[]), use_container_width=True)
    if not msgs:
        c1.markdown("**Try asking:**")
        cols = st.columns(2)
        for i, q in enumerate(SUGGEST):
            cols[i % 2].button(q, key=f"sg{i}", on_click=lambda q=q: st.session_state.update(pending=q), use_container_width=True)
    for m in msgs:
        with st.chat_message(m["role"]):
            _render(m)
    q = st.chat_input("Ask about any government scheme…") or st.session_state.pop("pending", None)
    if q:
        msgs.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner("Searching official documents and generating answer…"):
                try:
                    r = rag.answer(q)
                    m = {"role": "assistant", "content": r["answer"], "sources": r["hits"]}
                except rag.RagError as err:
                    m = {"role": "assistant", "content": f"⚠️ {err}", "sources": []}
            _render(m)
        msgs.append(m)


# ---------------------------------------------------------------- Search
def search():
    ui.header("Search Schemes", "Semantic AI search across indexed government scheme documents.")
    if no_docs():
        return
    q = st.text_input("Search", placeholder="Search government schemes...", label_visibility="collapsed")
    c = st.columns(4)
    f = {"state": c[0].selectbox("State", ["Any"] + STATES),
         "category": c[1].selectbox("Category", ["Any"] + rag.options("category")),
         "occupation": c[2].selectbox("Occupation", ["Any"] + rag.options("occupation")),
         "scheme_type": c[3].selectbox("Scheme type", ["Any"] + rag.options("scheme_type"))}
    if not q:
        st.caption("Enter a query, e.g. “loan for women entrepreneurs” or “support for farmers”.")
        return
    try:
        hits = rag.retrieve(q, 8, f)
        rag.log_query(q, hits, "search")
    except rag.RagError as err:
        st.error(str(err))
        return
    if not hits:
        st.warning("No matching schemes found. Try different keywords or relax the filters.")
    for i, h in enumerate(hits):
        m = h["meta"]
        ui.scheme_card(m["scheme"], {"Summary": h["text"][:220] + "…", "Relevance": h["score"]}, m["file"])
        with st.expander("View Details"):
            st.write(h["text"])
            st.caption(f"{m['state']} · {m['category']} · {m['occupation']} · {m['scheme_type']}")


# ---------------------------------------------------------------- Eligibility
def eligibility():
    ui.header("Eligibility Checker", "Tell us about yourself to find schemes that may match your profile.")
    if no_docs():
        return
    with st.form("elig"):
        st.markdown("**Step 1 · Personal details**")
        a, b, c = st.columns(3)
        age = a.number_input("Age", 1, 100, 21)
        gender = b.selectbox("Gender", ["Male", "Female", "Other"])
        cat = c.selectbox("Category", ["General", "OBC", "SC", "ST", "EWS", "Minority"])
        st.markdown("**Step 2 · Education & income**")
        a, b, c = st.columns(3)
        occ = a.selectbox("Occupation", ["Student", "Farmer", "Entrepreneur", "Unemployed", "Salaried", "Self-employed", "Homemaker", "Other"])
        edu = b.selectbox("Education", ["Below 10th", "10th", "12th", "Diploma", "B.Tech / Degree", "Postgraduate", "Other"])
        inc = c.number_input("Annual Income (₹)", 0, 100000000, 150000, step=10000)
        st.markdown("**Step 3 · Location & additional information**")
        a, b = st.columns(2)
        state = a.selectbox("State", STATES[1:], index=STATES[1:].index("Tamil Nadu"))
        dist = b.text_input("District")
        extra = st.text_area("Additional information", placeholder="e.g. first-generation graduate, own 2 acres of land…")
        go = st.form_submit_button("Find Eligible Schemes", type="primary", use_container_width=True)
    if not go:
        return
    p = dict(age=age, gender=gender, category=cat, occupation=occ, education=edu, income=inc, state=state, district=dist, extra=extra)
    with st.spinner("Matching your profile against indexed scheme documents…"):
        try:
            r = rag.eligibility(p)
        except rag.RagError as err:
            st.error(str(err))
            return
    if not r["schemes"]:
        st.warning("No clearly matching schemes were found in the indexed documents for this profile.")
    for s in r["schemes"]:
        ui.scheme_card(s.get("name", "Scheme"), {"Eligibility": s.get("eligibility"), "Benefits": s.get("benefits"),
                       "Required Documents": s.get("documents") if isinstance(s.get("documents"), str) else ", ".join(s.get("documents") or []),
                       "Why you may qualify": s.get("why")}, s.get("source", ""))
    ui.sources(r["hits"])
    ui.disclaimer()


# ---------------------------------------------------------------- Compare
def compare():
    ui.header("Compare Schemes", "Side-by-side comparison built from retrieved document content.")
    if no_docs():
        return
    pick = st.multiselect("Select 2–3 schemes", rag.schemes(), max_selections=3)
    if len(pick) < 2:
        st.caption("Pick at least two schemes.")
        return
    if st.button("Compare", type="primary"):
        with st.spinner("Retrieving and comparing…"):
            try:
                data = rag.compare(pick)
            except rag.RagError as err:
                st.error(str(err))
                return
        df = pd.DataFrame({n: [data[n].get(f, "Not found in documents") for f in rag.COMPARE_FIELDS] for n in pick},
                          index=rag.COMPARE_FIELDS)
        df.index.name = "Feature"
        st.table(df.map(lambda x: ", ".join(x) if isinstance(x, list) else str(x)))
        ui.disclaimer()


# ---------------------------------------------------------------- Upload
def upload():
    ui.header("Upload Documents", "Add official scheme documents to the knowledge base (admin only).")
    if not require_admin():
        return
    files = st.file_uploader("PDF, TXT or DOCX", type=["pdf", "txt", "docx"], accept_multiple_files=True)
    with st.expander("Optional metadata (used for search filters)"):
        a, b, c = st.columns(3)
        scheme = a.text_input("Scheme name (blank = auto-detect)")
        state = b.selectbox("State", STATES, key="u_state")
        stype = c.text_input("Scheme type", "General")
        d, e = st.columns(2)
        occ = d.text_input("Occupation", "Any")
        cat = e.text_input("Category", "Any")
    if files and st.button("Process & Index", type="primary"):
        for f in files:
            bar, msg = st.progress(0.0), st.empty()
            try:
                rag.ingest(f.name, f.getvalue(), dict(scheme=scheme if len(files) == 1 else "", state=state,
                           scheme_type=stype, occupation=occ, category=cat),
                           progress=lambda p, m: (bar.progress(p), msg.caption(f"{f.name}: {m}")))
                st.success(f"✅ {f.name}: Document indexed successfully.")
            except rag.RagError as err:
                st.error(f"❌ {err}")
            except Exception as err:
                st.error(f"❌ Unexpected error while processing {f.name}: {err}")
    _doc_table()


def _doc_table():
    reg = rag.registry()
    if reg:
        df = pd.DataFrame(reg.values())[["file", "type", "uploaded", "status", "chunks", "ocr"]]
        df.columns = ["File name", "Type", "Upload date", "Index status", "Chunks", "OCR used"]
        st.dataframe(df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------- Repository
def repository():
    ui.header("Knowledge Repository", "All documents indexed in ChromaDB.")
    s = rag.stats()
    a, b, c = st.columns(3)
    a.metric("Total documents", s["docs"])
    b.metric("Total chunks", s["chunks"])
    c.metric("Last indexed", s["last"]["file"] if s["last"] else "—")
    if no_docs():
        return
    admin = st.session_state.get("admin")
    if not admin:
        st.caption("🔒 Delete / Re-index require admin login (see Admin Dashboard).")
    for d in sorted(rag.registry().values(), key=lambda x: x["uploaded"], reverse=True):
        with st.container(border=True):
            c = st.columns([4, 2, 1, 1, 1, 1, 1])
            c[0].markdown(f"**{d['file']}**  \n<span style='color:#667'>{d['scheme']}</span>", unsafe_allow_html=True)
            c[1].caption(f"{d['state']} · {d['scheme_type']}")
            c[2].caption(f"{d['chunks']} chunks")
            c[3].markdown(f"<span class='badge'>{d['status']}</span>", unsafe_allow_html=True)
            if c[4].button("View", key="v" + d["id"]):
                st.session_state.view = d["id"]
            if admin:
                if c[5].button("Delete", key="d" + d["id"]):
                    rag.delete_doc(d["id"])
                    st.rerun()
                if c[6].button("Re-index", key="r" + d["id"]):
                    try:
                        with st.spinner("Re-indexing…"):
                            rag.reindex_doc(d["id"])
                        st.rerun()
                    except rag.RagError as err:
                        st.error(str(err))
            if st.session_state.get("view") == d["id"]:
                for t in rag.doc_chunks(d["id"], 10):
                    st.caption(t[:500])


# ---------------------------------------------------------------- Checklist
def checklist():
    ui.header("Application Checklist", "Documents and steps needed to apply, taken from the scheme documents.")
    if no_docs():
        return
    name = st.selectbox("Choose a scheme", rag.schemes())
    if st.button("Generate checklist", type="primary"):
        with st.spinner("Reading scheme documents…"):
            try:
                r = rag.checklist(name)
            except rag.RagError as err:
                st.error(str(err))
                return
        st.markdown("#### 📄 Documents required")
        for i, d in enumerate(r.get("documents") or ["Not found in documents"]):
            st.checkbox(str(d), key=f"cd{i}")
        st.markdown("#### 🪜 Application steps")
        for i, d in enumerate(r.get("steps") or ["Not found in documents"], 1):
            st.markdown(f"{i}. {d}")
        ui.disclaimer()


# ---------------------------------------------------------------- Evaluation
def evaluation():
    ui.header("RAG Evaluation", "Measure how well retrieval finds the correct scheme documents.")
    if no_docs():
        return
    k = st.slider("K (retrieved chunks)", 1, 10, 5)
    custom = st.text_area("Optional custom test cases (one per line: question | expected scheme name)")
    cases = [tuple(x.strip() for x in l.split("|", 1)) for l in custom.splitlines() if "|" in l] or rag.default_cases()
    st.caption(f"{len(cases)} test cases" + ("" if custom.strip() else " (auto-generated from indexed schemes)"))
    if st.button("Run evaluation", type="primary"):
        with st.spinner("Evaluating retrieval…"):
            try:
                rows = rag.evaluate(cases, k)
            except rag.RagError as err:
                st.error(str(err))
                return
        df = pd.DataFrame(rows)
        a, b, c = st.columns(3)
        a.metric(f"Precision@{k}", f"{df['Precision@K'].mean():.2f}")
        b.metric(f"Recall@{k}", f"{df['Recall@K'].mean():.2f}")
        c.metric("F1 Score", f"{df['F1'].mean():.2f}")
        st.bar_chart(pd.DataFrame({"Score": [df["Precision@K"].mean(), df["Recall@K"].mean(), df["F1"].mean()]},
                                  index=["Precision", "Recall", "F1"]))
        st.dataframe(df, use_container_width=True, hide_index=True)
    with st.expander("What is Precision?"):
        st.write("Of the K chunks retrieved, the fraction that come from the correct scheme document. High precision = little irrelevant context.")
    with st.expander("What is Recall?"):
        st.write("Whether the correct scheme document was found at all in the top K results (1 = found, 0 = missed). Averaged over test cases.")
    with st.expander("What is F1?"):
        st.write("The harmonic mean of precision and recall: 2·P·R / (P+R). It balances both measures in a single score.")


# ---------------------------------------------------------------- Admin
def admin():
    ui.header("Admin Dashboard", "System health and usage analytics.")
    if not require_admin():
        return
    st.button("Log out", on_click=lambda: st.session_state.update(admin=False))
    s = rag.stats()
    cols = st.columns(5)
    for c, (l, v) in zip(cols, [("Documents", s["docs"]), ("Chunks", s["chunks"]), ("Queries", s["queries"]),
                                ("Avg retrieval score", s["avg_score"]), ("System", "Online")]):
        c.metric(l, v)
    st.markdown("#### System status")
    st.write(f"- Gemini API key: {'✅ configured' if rag.get_secret('GEMINI_API_KEY') else '❌ missing'}")
    st.write(f"- Embedding model: {'✅ loaded' if rag.get_embedder() else '❌ not available'} ({rag.EMBED_MODEL})")
    try:
        rag.get_collection()
        st.write("- ChromaDB: ✅ connected")
    except rag.RagError:
        st.write("- ChromaDB: ❌ unavailable")
    log = rag.query_log()
    a, b = st.columns(2)
    with a:
        st.markdown("**Queries over time**")
        if log:
            df = pd.DataFrame(log)
            df["day"] = pd.to_datetime(df["ts"]).dt.date
            st.line_chart(df.groupby("day").size())
        else:
            st.caption("No queries yet.")
    reg = pd.DataFrame(rag.registry().values())
    with b:
        st.markdown("**Documents indexed (chunks per document)**")
        if not reg.empty:
            st.bar_chart(reg.set_index("file")["chunks"])
        else:
            st.caption("No documents yet.")
    st.markdown("**Scheme distribution by type**")
    if not reg.empty:
        st.bar_chart(reg.groupby("scheme_type").size())
    if st.button("Clear query log"):
        rag.clear_log()
        st.rerun()


# ---------------------------------------------------------------- About
def about():
    ui.header("About JANASAHAY AI", "AI-Powered Government Scheme Assistant")
    st.markdown("### Problem Statement")
    st.write("Government welfare information is often distributed across large and complex documents. "
             "Citizens may struggle to identify schemes relevant to their circumstances.")
    st.markdown("### Solution")
    st.write("JANASAHAY AI uses Retrieval-Augmented Generation to retrieve relevant government information "
             "and generate grounded answers.")
    st.markdown("### Technology")
    st.markdown("".join(f'<span class="badge">{t}</span>' for t in
                        ["Python", "Streamlit", "Google Gemini", "ChromaDB", "Sentence Transformers (all-MiniLM-L6-v2)", "PyPDF", "Tesseract OCR"]),
                unsafe_allow_html=True)
    st.markdown("### RAG Architecture")
    flow = ["Documents", "Processing", "Chunking", "Embeddings", "ChromaDB", "Retrieval", "Gemini", "Answer + Sources"]
    st.markdown('<div class="flow">' + "<b>→</b>".join(f"<div>{x}</div>" for x in flow) + "</div>", unsafe_allow_html=True)
    st.write("")
    ui.disclaimer()


PAGES = {"🏠 Home": home, "🤖 AI Assistant": assistant, "🔎 Search Schemes": search, "🎯 Eligibility Checker": eligibility,
         "📊 Compare Schemes": compare, "📄 Upload Documents": upload, "📚 Knowledge Repository": repository,
         "📋 Application Checklist": checklist, "📈 Evaluation": evaluation, "⚙️ Admin Dashboard": admin, "ℹ️ About": about}
