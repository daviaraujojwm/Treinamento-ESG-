from __future__ import annotations

import base64
import datetime as dt
import hashlib
import re
import unicodedata
from collections import Counter
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -------------------------------------------------------------------
# Configuração geral
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Treinamentos ESG | EcoVadis",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

META = 233
LABELS = {
    "boas praticas ambientais": "Boas Práticas Ambientais",
    "responsabilidade socioambiental": "Responsabilidade Socioambiental",
    "declive na etica do trabalho": "Declive na Ética do Trabalho",
    "etica no ambiente de trabalho": "Ética no Ambiente de Trabalho",
    "direitos humanos": "Direitos Humanos",
    "gestao responsavel": "Gestão Responsável",
}
CORES = ["#1b7a33", "#7cb518", "#e0a800", "#0f9d8a", "#2f6db3", "#d7201f"]
LOGO_BASE64 = "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"
LOGO_MIME = "image/jpeg"


def norm(value) -> str:
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = value.encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", value).strip()


def parse_date(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (dt.datetime, dt.date, pd.Timestamp)):
        return pd.Timestamp(value).date()
    if isinstance(value, (int, float)):
        # Serial de data do Excel
        return (dt.datetime(1899, 12, 30) + dt.timedelta(days=float(value))).date()
    try:
        return pd.to_datetime(value, dayfirst=True, errors="raise").date()
    except Exception:
        return None


def find_col(headers, *keys):
    for idx, header in enumerate(headers):
        if any(key in header for key in keys):
            return idx
    return None


def process_workbook(uploaded_file):
    """Replica a regra do conversor original: uma resposta por pessoa/treinamento."""
    uploaded_file.seek(0)
    workbook = pd.ExcelFile(uploaded_file)
    records = []
    stats = {}
    sheet_order = []

    for sheet_name in workbook.sheet_names:
        sheet_order.append(sheet_name)
        frame = pd.read_excel(workbook, sheet_name=sheet_name, header=0, dtype=object)
        headers = [norm(col) for col in frame.columns]

        i_nome = find_col(headers, "nome completo")
        i_corp = find_col(headers, "e-mail co", "email co")
        i_email = headers.index("email") if "email" in headers else None
        i_data = find_col(headers, "hora de conclusao")

        title = LABELS.get(norm(sheet_name), sheet_name.strip())
        seen = set()
        kept = duplicated = blank = 0

        for _, row in frame.iterrows():
            values = list(row)
            if all(pd.isna(v) for v in values):
                continue

            nome = values[i_nome] if i_nome is not None and i_nome < len(values) else ""
            mail = values[i_corp] if i_corp is not None and i_corp < len(values) else ""

            if (pd.isna(mail) or not str(mail).strip()) and i_email is not None:
                fallback = values[i_email]
                if not pd.isna(fallback) and "@" in str(fallback):
                    mail = fallback

            nome = "" if pd.isna(nome) else norm(nome)
            mail = "" if pd.isna(mail) else norm(mail)

            if not nome and not mail:
                blank += 1
                continue

            key = mail or nome
            if key in seen:
                duplicated += 1
                continue

            seen.add(key)
            raw_date = values[i_data] if i_data is not None and i_data < len(values) else None
            date_value = parse_date(raw_date)
            person_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:10]

            records.append({
                "treinamento": title,
                "data": date_value.isoformat() if date_value else "",
                "pessoa": person_id,
            })
            kept += 1

        stats[title] = {
            "conclusoes": kept,
            "duplicadas": duplicated,
            "em_branco": blank,
        }

    conclusions = pd.DataFrame(records, columns=["treinamento", "data", "pessoa"])
    return conclusions, stats, sheet_order


def build_metrics(conclusions):
    if conclusions.empty:
        empty = pd.DataFrame(columns=["treinamento", "concluidos", "pendentes", "pct"])
        return empty, {}, pd.DataFrame(columns=["data", "treinamento", "acumulado", "pct"]), pd.DataFrame(columns=["data", "conclusoes_dia"])

    training_order = list(dict.fromkeys(conclusions["treinamento"].tolist()))
    by_training = []
    for training in training_order:
        count = conclusions.loc[
            conclusions["treinamento"] == training, "pessoa"
        ].nunique()
        by_training.append({
            "treinamento": training,
            "concluidos": int(count),
            "pendentes": max(META - int(count), 0),
            "pct": count / META,
        })
    by_training = pd.DataFrame(by_training)

    by_person = conclusions.groupby("pessoa")["treinamento"].nunique()
    total_trainings = len(by_training)
    people = int(by_person.size)
    completed_all = int((by_person >= total_trainings).sum()) if total_trainings else 0
    avg_reach = float(by_training["pct"].mean()) if total_trainings else 0.0
    lowest = by_training.loc[by_training["pct"].idxmin()] if total_trainings else None
    valid_dates = conclusions.loc[conclusions["data"].astype(bool), "data"]
    latest = valid_dates.max() if not valid_dates.empty else ""

    summary = {
        "pessoas": people,
        "pessoas_pct": people / META,
        "completos": completed_all,
        "completos_pct": completed_all / META,
        "conclusoes": int(by_training["concluidos"].sum()) if total_trainings else 0,
        "alcance_medio": avg_reach,
        "menor_nome": lowest["treinamento"] if lowest is not None else "—",
        "menor_pct": float(lowest["pct"]) if lowest is not None else 0.0,
        "ultimo_dia": latest,
    }

    # Evolução acumulada: primeira conclusão de cada pessoa em cada treinamento.
    dated = conclusions[conclusions["data"].astype(bool)].copy()
    evolution_rows = []
    if not dated.empty:
        dated = dated.sort_values("data")
        first_dates = dated.groupby(["treinamento", "pessoa"], as_index=False)["data"].min()
        days = sorted(first_dates["data"].unique())
        for training in training_order:
            dates = first_dates.loc[first_dates["treinamento"] == training, "data"].tolist()
            for day in days:
                reached = sum(date <= day for date in dates)
                evolution_rows.append({
                    "data": day,
                    "treinamento": training,
                    "acumulado": reached,
                    "pct": reached / META,
                })
    evolution = pd.DataFrame(evolution_rows, columns=["data", "treinamento", "acumulado", "pct"])

    per_day = (
        dated.groupby("data").size().reset_index(name="conclusoes_dia")
        if not dated.empty
        else pd.DataFrame(columns=["data", "conclusoes_dia"])
    )
    return by_training, summary, evolution, per_day


def pct(value):
    return f"{value:.1%}".replace(".", ",")


def integer(value):
    return f"{int(value):,}".replace(",", ".")


def status_label(value):
    if value >= 1:
        return "Meta atingida", "ok"
    if value >= 0.5:
        return "Em andamento", "mid"
    return "Abaixo de 50%", "low"


def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');
    .stApp { background: var(--background-color); }
    .block-container { max-width: 1380px; padding-top: 2rem; padding-bottom: 3rem; }
    #MainMenu, footer { visibility: hidden; }
    .jw-upload-box { text-align:center; padding:1rem 1rem .25rem; margin-top:.35rem; }
    .jw-upload-title { color:var(--text-color); font-size:1.08rem; font-weight:700; }
    .jw-upload-note { color:var(--text-color); opacity:.72; font-size:.88rem; margin-top:.2rem; }
    div[data-testid="stFileUploader"] {
      border:1.5px dashed #2f9a44; border-radius:14px; padding:1rem;
      background:rgba(47,154,68,.055);
    }
    div[data-testid="stFileUploader"] section { border:0; background:transparent; }
    .jw { --green-900:#0f3d1c; --green-700:#1b6b2f; --green-500:#2f9a44;
          --green-300:#8fd19e; --yellow:#f2c200; --done:#23863a; --todo:#dfeee2;
          --tint:#f1f8f2; color:var(--text-color); font-family:'DM Sans',sans-serif;
          display:grid; gap:1.35rem; max-width:1320px; margin:0 auto; }
    .jw-band { position:relative; overflow:hidden; border-radius:18px; color:#fff;
      background:radial-gradient(120% 140% at 100% 0%,#2f9a44 0%,#1b6b2f 45%,#0f3d1c 100%);
      display:grid; grid-template-columns:auto 1fr auto; gap:1.4rem; align-items:center; padding:1.7rem; }
    .jw-band:after { content:""; position:absolute; inset:auto -10% -60% 40%; height:120%;
      border-radius:50%; background:rgba(242,194,0,.10); pointer-events:none; }
    .jw-logo { background:#fff; border-radius:10px; padding:8px 14px; display:flex; align-items:center;
      box-shadow:0 6px 20px rgba(0,0,0,.18); position:relative; z-index:1; }
    .jw-logo img { display:block; height:64px; width:auto; max-width:190px; }
    .jw-head { min-width:0; display:grid; gap:6px; position:relative; z-index:1; }
    .jw-eyebrow { font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:#bfe8c8; font-weight:600; }
    .jw-title { margin:0; font-family:'DM Serif Display',serif; font-weight:400;
      font-size:clamp(1.6rem,3.2vw,2.4rem); line-height:1.1; }
    .jw-title em { font-style:normal; color:#f2c200; }
    .jw-sub { margin:0; font-size:.9rem; color:#d9f0de; }
    .jw-medal { position:relative; z-index:1; display:grid; place-items:center; text-align:center;
      width:112px; height:112px; border-radius:50%;
      background:radial-gradient(circle at 35% 30%,#fff6c9 0%,#f2c200 45%,#b98a00 100%);
      color:#3a2b00; box-shadow:0 0 0 4px rgba(255,255,255,.25),0 8px 18px rgba(0,0,0,.25);
      font-weight:700; font-size:.82rem; line-height:1.15; padding:10px; }
    .jw-medal b { display:block; font-size:1.05rem; }
    .jw-takeaway { margin:0; font-size:1.08rem; line-height:1.55; max-width:75ch; }
    .jw-takeaway strong { color:#23863a; font-weight:700; }
    .jw-kpi { background:var(--secondary-background-color); border:1px solid rgba(128,128,128,.20);
      border-radius:12px; padding:1.15rem; min-height:138px; display:flex; flex-direction:column; gap:7px; }
    .jw-kpi.lead { background:#f1f8f2; border-color:rgba(35,134,58,.35); }
    .jw-kpi-label { font-size:.72rem; color:var(--secondary-text-color); letter-spacing:.04em; text-transform:uppercase; }
    .jw-kpi-value { font-family:'DM Serif Display',serif; font-size:2.55rem; line-height:1.05; color:var(--text-color); }
    .jw-kpi.lead .jw-kpi-value { color:#23863a; }
    .jw-kpi-note { font-size:.75rem; color:var(--secondary-text-color); line-height:1.4; }
    .jw-meter { height:8px; border-radius:99px; background:#dfeee2; overflow:hidden; margin-top:4px; }
    .jw-meter-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#2f9a44,#f2c200); }
    .jw-section-head { display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between; gap:.8rem; margin-bottom:.8rem; }
    .jw-h2 { margin:0; font-size:1.35rem; font-weight:600; }
    .jw-card-title { margin:0; font-size:1.08rem; font-weight:600; }
    .jw-card-note { margin:.25rem 0 .8rem; font-size:.78rem; color:var(--secondary-text-color); }
    .jw-pie-card { background:var(--secondary-background-color); border:1px solid rgba(128,128,128,.20);
      border-radius:12px; padding:1rem; height:100%; }
    .jw-pie-top { display:flex; justify-content:space-between; align-items:flex-start; gap:8px; min-height:42px; }
    .jw-pie-name { margin:0; font-size:.9rem; font-weight:600; line-height:1.3; }
    .jw-pill { font-size:10px; font-weight:700; padding:4px 9px; border-radius:99px; white-space:nowrap; }
    .jw-pill.ok { background:rgba(35,134,58,.16); color:#23863a; }
    .jw-pill.mid { background:rgba(224,168,0,.17); color:#a77b00; }
    .jw-pill.low { background:rgba(215,32,31,.13); color:#d7201f; }
    .jw-pie-facts { display:grid; gap:4px; font-size:.76rem; color:var(--secondary-text-color); }
    .jw-pie-pct { font-family:'DM Serif Display',serif; font-size:2rem; color:#23863a; line-height:1.1; }
    .jw-legend { display:flex; flex-wrap:wrap; gap:6px 16px; font-size:.75rem; color:var(--secondary-text-color); }
    .jw-swatch { width:10px; height:10px; display:inline-block; border-radius:3px; margin-right:6px; }
    .jw-table { width:100%; border-collapse:collapse; font-size:.88rem; }
    .jw-table th { text-align:left; font-size:.7rem; color:var(--secondary-text-color); text-transform:uppercase;
      letter-spacing:.04em; padding:9px 10px; border-bottom:1px solid rgba(128,128,128,.25); }
    .jw-table td { padding:11px 10px; border-bottom:1px solid rgba(128,128,128,.16); }
    .jw-table .num { text-align:right; font-variant-numeric:tabular-nums; }
    .jw-foot { font-size:.78rem; color:var(--secondary-text-color); }
    .jw-foot summary { cursor:pointer; font-weight:600; }
    .jw-foot dl { display:grid; grid-template-columns:max-content 1fr; gap:7px 16px; margin:12px 0 0; }
    .jw-foot dt { font-weight:700; color:var(--text-color); }
    .jw-foot dd { margin:0; }
    @media(max-width:760px) { .jw-band {grid-template-columns:1fr;} .jw-medal{display:none;}
      .jw-logo img{height:52px;} .jw-foot dl{grid-template-columns:1fr;} }
    </style>
    """, unsafe_allow_html=True)


def render_header(summary):
    logo_html = ""
    if LOGO_BASE64:
        logo_html = f'<div class="jw-logo"><img src="data:{LOGO_MIME};base64,{LOGO_BASE64}" alt="JWM Soluções Logísticas"></div>'
    last_date = pd.to_datetime(summary["ultimo_dia"]).strftime("%d/%m/%Y") if summary["ultimo_dia"] else "—"
    st.markdown(f"""
    <div class="jw">
      <header class="jw-band" id="topo">
        {logo_html}
        <div class="jw-head">
          <span class="jw-eyebrow">EcoVadis Sustainability Rating · TrilhaZUM Kolmeia</span>
          <h1 class="jw-title">Treinamentos <em>ESG</em> da EcoVadis</h1>
          <p class="jw-sub">Painel de alcance dos 6 treinamentos · meta de 100% dos {integer(META)} colaboradores · dados até {last_date}</p>
        </div>
        <div class="jw-medal"><div>Rumo à<b>medalha Prata</b></div></div>
      </header>
    </div>
    """, unsafe_allow_html=True)


def render_kpi(label, value, note, lead=False, progress=None):
    cls = "jw-kpi lead" if lead else "jw-kpi"
    meter = ""
    if progress is not None:
        meter = f'<div class="jw-meter"><div class="jw-meter-fill" style="width:{min(100, max(0, progress*100)):.1f}%"></div></div>'
    st.markdown(
        f'<div class="{cls}"><span class="jw-kpi-label">{label}</span>'
        f'<span class="jw-kpi-value">{value}</span>{meter}'
        f'<span class="jw-kpi-note">{note}</span></div>',
        unsafe_allow_html=True,
    )


def style_plot(fig, height=250):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,.18)", zeroline=False)
    return fig


def render_dashboard(conclusions, stats):
    by_training, summary, evolution, per_day = build_metrics(conclusions)
    render_header(summary)

    lowest_name = summary["menor_nome"]
    st.markdown(
        f'<p class="jw-takeaway">Até agora, <strong>{integer(summary["pessoas"])}</strong> colaboradores fizeram ao menos um treinamento e '
        f'<strong>{integer(summary["completos"])}</strong> já concluíram os seis. O alcance médio é de '
        f'<strong>{pct(summary["alcance_medio"])}</strong>, e o treinamento que mais precisa de atenção é '
        f'<strong>{lowest_name}</strong>, com <strong>{pct(summary["menor_pct"])}</strong> de alcance.</p>',
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi("Alcance médio dos treinamentos", pct(summary["alcance_medio"]),
                   "Média do % de colaboradores que concluiu cada treinamento",
                   lead=True, progress=summary["alcance_medio"])
    with k2:
        render_kpi("Colaboradores participantes", integer(summary["pessoas"]),
                   f"Fizeram ao menos 1 dos 6 treinamentos ({pct(summary['pessoas_pct'])} da equipe)")
    with k3:
        render_kpi("Concluíram os 6 treinamentos", integer(summary["completos"]),
                   f"{pct(summary['completos_pct'])} da equipe com a trilha completa")
    with k4:
        render_kpi("Conclusões registradas", integer(summary["conclusoes"]),
                   "Soma dos 6 treinamentos, sem respostas duplicadas")

    st.markdown("""
    <div class="jw-section-head" style="margin-top:1.3rem">
      <h2 class="jw-h2">Alcance por treinamento</h2>
      <div class="jw-legend">
        <span><i class="jw-swatch" style="background:#23863a"></i>Concluíram</span>
        <span><i class="jw-swatch" style="background:#dfeee2"></i>Pendentes</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if by_training.empty:
        st.info("Não há registros para exibir.")
    else:
        pie_cols = st.columns(min(3, len(by_training)))
        for idx, row in by_training.iterrows():
            col = pie_cols[idx % len(pie_cols)]
            label, cls = status_label(row["pct"])
            with col:
                st.markdown(
                    f'<div class="jw-pie-card"><div class="jw-pie-top">'
                    f'<h3 class="jw-pie-name">{row["treinamento"]}</h3>'
                    f'<span class="jw-pill {cls}">{label}</span></div>',
                    unsafe_allow_html=True,
                )
                fig = go.Figure(data=[go.Pie(
                    labels=["Concluíram", "Pendentes"],
                    values=[row["concluidos"], row["pendentes"]],
                    hole=0,
                    sort=False,
                    marker=dict(colors=["#23863a", "#dfeee2"], line=dict(color="rgba(255,255,255,.8)", width=1)),
                    textinfo="none",
                    hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
                )])
                fig.update_layout(
                    height=165, width=165, margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                )
                left, right = st.columns([1, 1.15], vertical_alignment="center")
                with left:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"pie_{idx}")
                with right:
                    st.markdown(
                        f'<div class="jw-pie-facts"><div class="jw-pie-pct">{pct(row["pct"])}</div>'
                        f'<div>🟢 {integer(row["concluidos"])} de {integer(META)} concluíram</div>'
                        f'<div>◻ {integer(row["pendentes"])} pendentes</div></div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="jw-card-title">Evolução do alcance</div><div class="jw-card-note">% acumulado de colaboradores que concluiu cada treinamento, dia a dia</div>', unsafe_allow_html=True)
        if not evolution.empty:
            fig = px.line(
                evolution, x="data", y="pct", color="treinamento",
                color_discrete_sequence=CORES, markers=True,
            )
            fig.update_yaxes(tickformat=".0%", rangemode="tozero")
            st.plotly_chart(style_plot(fig, 300), use_container_width=True, config={"displayModeBar": False})
        else:
            st.caption("Sem datas de conclusão válidas para montar a evolução.")
    with right:
        st.markdown('<div class="jw-card-title">Conclusões por dia</div><div class="jw-card-note">Total de treinamentos concluídos em cada dia, somando os 6</div>', unsafe_allow_html=True)
        if not per_day.empty:
            fig = px.bar(per_day, x="data", y="conclusoes_dia", text="conclusoes_dia")
            fig.update_traces(marker_color="#23863a", textposition="outside", cliponaxis=False)
            fig.update_yaxes(rangemode="tozero", title=None)
            st.plotly_chart(style_plot(fig, 300), use_container_width=True, config={"displayModeBar": False})
        else:
            st.caption("Sem datas de conclusão válidas para montar o gráfico.")

    st.markdown('<div class="jw-card-title" style="margin-top:1.3rem">Ranking dos treinamentos</div><div class="jw-card-note">Do maior para o menor alcance. Pendentes = meta de colaboradores menos quem já concluiu.</div>', unsafe_allow_html=True)
    if not by_training.empty:
        ranking = by_training.sort_values("pct", ascending=False).copy()
        ranking["Concluíram"] = ranking["concluidos"].map(integer)
        ranking["Pendentes"] = ranking["pendentes"].map(integer)
        ranking["Alcance"] = ranking["pct"].map(pct)
        st.dataframe(
            ranking[["treinamento", "Concluíram", "Pendentes", "Alcance"]].rename(columns={"treinamento": "Treinamento"}),
            use_container_width=True, hide_index=True,
        )

    with st.expander("Como os números são calculados"):
        st.markdown(
            f"""
            **Meta:** 100% dos {integer(META)} colaboradores da JWM em cada um dos 6 treinamentos.

            **Concluíram:** pessoas distintas que enviaram o formulário do treinamento. Respostas repetidas da mesma pessoa contam uma vez (identificação pelo e-mail corporativo; pelo nome quando o e-mail falta).

            **Deixados de fora:** respostas em branco, sem nome e sem e-mail.

            **Privacidade:** o painel não guarda nomes nem e-mails: cada pessoa vira um código anônimo, usado só para não contar a mesma pessoa duas vezes.
            """
        )

    with st.expander("Conferência da importação"):
        audit = pd.DataFrame([
            {"Treinamento": name, **values} for name, values in stats.items()
        ])
        st.dataframe(audit, use_container_width=True, hide_index=True)
        st.caption(
            f"Pessoas únicas identificadas: {conclusions['pessoa'].nunique() if not conclusions.empty else 0} · "
            f"Com os 6 treinamentos: {summary['completos']}"
        )

    csv_bytes = conclusions.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Baixar base tratada (CSV)",
        data=csv_bytes,
        file_name="conclusoes_ecovadis.csv",
        mime="text/csv",
    )


# -------------------------------------------------------------------
# Interface Streamlit
# -------------------------------------------------------------------
inject_styles()

with st.sidebar:
    st.markdown("## 🌿 Painel EcoVadis")
    st.markdown("Painel de acompanhamento dos treinamentos ESG.")
    st.divider()
    st.caption(f"Meta configurada: {META} colaboradores")
    st.caption("Os nomes e e-mails não são exibidos no painel; são convertidos em códigos anônimos.")

# Botão de envio em destaque no painel principal.
upload_left, upload_center, upload_right = st.columns([1, 2, 1])
with upload_center:
    st.markdown(
        """
        <div class="jw-upload-box">
          <div class="jw-upload-title">Atualizar dados do painel</div>
          <div class="jw-upload-note">Selecione a planilha Excel de respostas (.xlsx)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Selecionar planilha Excel",
        type=["xlsx"],
        help="Escolha o arquivo .xlsx com as respostas dos treinamentos.",
        key="planilha_ecovadis_upload",
    )

if uploaded is None:
    st.markdown("""
    <div class="jw">
      <header class="jw-band">
        <div class="jw-head">
          <span class="jw-eyebrow">EcoVadis Sustainability Rating · TrilhaZUM Kolmeia</span>
          <h1 class="jw-title">Treinamentos <em>ESG</em> da EcoVadis</h1>
          <p class="jw-sub">Painel de alcance dos 6 treinamentos · meta de 100% dos 233 colaboradores</p>
        </div>
        <div class="jw-medal"><div>Rumo à<b>medalha Prata</b></div></div>
      </header>
    </div>
    """, unsafe_allow_html=True)
    st.info("Para visualizar o painel, envie a planilha Excel utilizada nos treinamentos pelo campo à esquerda.")
else:
    try:
        conclusions, import_stats, sheets = process_workbook(uploaded)
        if conclusions.empty:
            st.warning("A planilha foi lida, mas não foram encontradas respostas com nome ou e-mail.")
        else:
            render_dashboard(conclusions, import_stats)
    except Exception as exc:
        st.error(f"Não foi possível processar a planilha: {exc}")
        st.exception(exc)
