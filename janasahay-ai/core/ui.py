"""JANASAHAY AI - theme, CSS and small HTML components."""
from html import escape as e

import streamlit as st

NAV = ["🏠 Home", "🤖 AI Assistant", "🔎 Search Schemes", "🎯 Eligibility Checker", "📊 Compare Schemes",
       "📄 Upload Documents", "📚 Knowledge Repository", "📋 Application Checklist", "📈 Evaluation",
       "⚙️ Admin Dashboard", "ℹ️ About"]

CSS = """
<style>
:root{--navy:#0B2447;--green:#138808;--saffron:#FF9933;--gray:#F5F7FA;--line:#E3E8EF}
#MainMenu,footer{visibility:hidden}
.block-container{padding-top:1.6rem;max-width:1150px}
html,body,[class*="css"]{font-family:'Inter','Segoe UI',sans-serif}
[data-testid="stSidebar"]{background:var(--navy)}
[data-testid="stSidebar"] *{color:#fff}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:.45rem .7rem;border-radius:10px;margin-bottom:2px;transition:background .15s}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(255,255,255,.12)}
.tricolor{height:5px;border-radius:4px;background:linear-gradient(90deg,#FF9933 33%,#fff 33% 66%,#138808 66%);margin-bottom:.8rem}
.brand{font-size:1.35rem;font-weight:800;letter-spacing:.5px}
.brand span{color:var(--saffron)}
.hero{background:linear-gradient(135deg,#0B2447 0%,#14407a 60%,#138808 140%);color:#fff;border-radius:20px;padding:2.6rem 2.2rem;margin-bottom:1.2rem;box-shadow:0 8px 24px rgba(11,36,71,.25)}
.hero h1{font-size:2.8rem;margin:0;font-weight:800;letter-spacing:1px;color:#fff}
.hero h1 span{color:var(--saffron)}
.hero .sub{font-size:1.15rem;opacity:.9;margin:.3rem 0 .8rem}
.hero .tag{display:inline-block;border-left:4px solid var(--saffron);padding-left:.8rem;font-style:italic;font-size:1.1rem}
.card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:1.2rem;box-shadow:0 2px 8px rgba(11,36,71,.06);transition:transform .15s,box-shadow .15s;height:100%}
.card:hover{transform:translateY(-3px);box-shadow:0 8px 20px rgba(11,36,71,.12)}
.card h4{margin:.2rem 0 .4rem;color:var(--navy)}
.card p{margin:0;color:#4a5568;font-size:.93rem}
.stat{background:#fff;border:1px solid var(--line);border-top:4px solid var(--saffron);border-radius:14px;padding:1rem;text-align:center;box-shadow:0 2px 8px rgba(11,36,71,.06)}
.stat .n{font-size:2rem;font-weight:800;color:var(--navy)}
.stat .l{font-size:.85rem;color:#5b6678}
.step{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1rem;text-align:center;height:100%}
.step .i{width:34px;height:34px;line-height:34px;border-radius:50%;background:var(--green);color:#fff;margin:0 auto .5rem;font-weight:700}
.step p{margin:0;font-size:.9rem;color:#334}
.ph{border-left:6px solid var(--green);padding:.2rem 0 .2rem 1rem;margin-bottom:1.2rem}
.ph h2{margin:0;color:var(--navy)}
.ph p{margin:0;color:#5b6678}
.badge{display:inline-block;background:#e8f5e9;color:var(--green);border-radius:20px;padding:.1rem .7rem;font-size:.78rem;font-weight:600;margin-right:.3rem}
.badge.o{background:#fff3e0;color:#c76a00}
.scheme{background:#fff;border:1px solid var(--line);border-left:6px solid var(--green);border-radius:14px;padding:1.1rem 1.3rem;margin-bottom:.9rem;box-shadow:0 2px 8px rgba(11,36,71,.05)}
.scheme h4{margin:0 0 .4rem;color:var(--navy)}
.scheme .k{font-weight:700;color:var(--navy)}
.flow{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;justify-content:center}
.flow div{background:var(--navy);color:#fff;padding:.5rem .9rem;border-radius:10px;font-size:.9rem}
.flow b{color:var(--saffron)}
.disc{background:#fff8e6;border:1px solid #ffd98a;border-radius:10px;padding:.7rem 1rem;font-size:.88rem;color:#7a5b00}
.stButton>button[kind="primary"]{background:var(--green);border:none;border-radius:10px;font-weight:600}
.stButton>button{border-radius:10px}
@media(max-width:700px){.hero h1{font-size:2rem}.hero{padding:1.6rem 1.2rem}}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def header(title: str, sub: str):
    st.markdown(f'<div class="ph"><h2>{e(title)}</h2><p>{e(sub)}</p></div>', unsafe_allow_html=True)


def hero():
    st.markdown('<div class="hero"><h1>JANASAHAY <span>AI</span></h1>'
                '<div class="sub">AI-Powered Government Scheme Assistant</div>'
                '<div class="tag">“Discover the Government Schemes You Deserve.”</div></div>', unsafe_allow_html=True)


def card(icon: str, title: str, text: str):
    st.markdown(f'<div class="card"><div style="font-size:1.8rem">{icon}</div><h4>{e(title)}</h4><p>{e(text)}</p></div>',
                unsafe_allow_html=True)


def stat(label: str, value):
    st.markdown(f'<div class="stat"><div class="n">{e(str(value))}</div><div class="l">{e(label)}</div></div>',
                unsafe_allow_html=True)


def step(n: int, text: str):
    st.markdown(f'<div class="step"><div class="i">{n}</div><p>{e(text)}</p></div>', unsafe_allow_html=True)


def scheme_card(title: str, rows: dict, source: str = ""):
    body = "".join(f'<div><span class="k">{e(k)}:</span> {e(str(v))}</div>' for k, v in rows.items() if v)
    src = f'<div style="margin-top:.4rem"><span class="badge">📎 {e(source)}</span></div>' if source else ""
    st.markdown(f'<div class="scheme"><h4>{e(title)}</h4>{body}{src}</div>', unsafe_allow_html=True)


def disclaimer():
    st.markdown('<div class="disc">⚠️ Eligibility shown is an initial AI-assisted indication. '
                'Please verify final eligibility with the official government authority.</div>', unsafe_allow_html=True)


def sources(hits: list[dict]):
    if not hits:
        return
    with st.expander(f"📎 Sources & retrieved content ({len(hits)})"):
        for i, h in enumerate(hits, 1):
            m = h["meta"]
            st.markdown(f'**[{i}] {m["scheme"]}** <span class="badge">{e(m["file"])}</span>'
                        f'<span class="badge o">relevance {h["score"]}</span>', unsafe_allow_html=True)
            st.caption(h["text"][:600] + ("…" if len(h["text"]) > 600 else ""))
