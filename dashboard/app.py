from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "bank_marketing_clean.csv"
SCORES_FILE = ROOT / "data" / "powerbi" / "model_scores.csv"
EVALUATION_FILE = ROOT / "data" / "powerbi" / "evaluation_predictions.csv"
IMPORTANCE_FILE = ROOT / "reports" / "generated" / "feature_importance.csv"
DECILE_FILE = ROOT / "reports" / "generated" / "decile_performance.csv"
METRICS_FILE = ROOT / "reports" / "generated" / "model_metrics.json"

LANGUAGES = {
    "English": "en",
    "简体中文": "zh_cn",
    "繁體中文": "zh_tw",
}

TEXT = {
    "en": {
        "title": "Bank Marketing Analytics",
        "subtitle": "Historical campaign analysis and pre-contact subscription propensity",
        "language": "Language",
        "filters": "Filters",
        "job": "Job",
        "channel": "Contact channel",
        "month": "Month",
        "all": "All",
        "contacts": "Campaign contacts",
        "subscriptions": "Subscriptions",
        "conversion": "Conversion rate",
        "attempts": "Avg. contact attempts",
        "overview": "Overview",
        "segments": "Customer segments",
        "efficiency": "Campaign efficiency",
        "model": "Model & lift",
        "priority": "Priority list",
        "monthly_title": "Monthly conversion and contact volume",
        "channel_title": "Channel conversion and contact volume",
        "conversion_axis": "Conversion rate",
        "volume_axis": "Contacts",
        "month_axis": "Month",
        "channel_axis": "Channel",
        "job_title": "Conversion by job",
        "age_title": "Conversion by age band",
        "job_axis": "Job",
        "age_axis": "Age band",
        "sample_warning": "Segments with fewer than 100 contacts are excluded from ranking.",
        "attempt_title": "Contact frequency and conversion",
        "previous_title": "Previous campaign outcome",
        "attempt_axis": "Contact intensity",
        "previous_axis": "Previous outcome",
        "model_note": "Call duration is excluded because it is only known after the call ends.",
        "selected_model": "Selected model",
        "roc_auc": "ROC-AUC",
        "pr_auc": "PR-AUC",
        "recall": "Recall",
        "lift_title": "Cumulative gain on the independent test set",
        "lift_x": "Share of prospects contacted",
        "lift_y": "Share of subscribers captured",
        "model_curve": "Model ranking",
        "random_curve": "Random targeting",
        "decile_title": "Response rate and lift by score decile",
        "decile": "Score decile",
        "response_rate": "Response rate",
        "lift": "Lift",
        "importance_title": "Top model signals",
        "importance": "Relative importance",
        "feature": "Feature",
        "simulator": "Campaign capacity simulator",
        "simulator_help": "Uses held-out historical outcomes to estimate how model-ranked targeting would have performed.",
        "capacity": "Prospects to contact",
        "cost": "Estimated cost per contact",
        "captured": "Historical subscribers captured",
        "capture_rate": "Subscriber capture rate",
        "target_conversion": "Targeted conversion rate",
        "cost_per_conversion": "Cost per captured subscriber",
        "random_expected": "Expected subscribers under random targeting",
        "contacts_avoided": "Contacts avoided versus contacting the full test set",
        "historical_only": "Historical holdout simulation, not a guarantee of future campaign results.",
        "priority_segment": "Priority segment",
        "high": "High priority",
        "medium": "Medium priority",
        "low": "Low priority",
        "download": "Download filtered list",
        "score": "Propensity score",
        "actual": "Historical outcome",
        "footer": "Portfolio demonstration using the UCI Bank Marketing dataset. Generated customer IDs represent campaign rows, not verified unique individuals.",
        "no_data": "No records match the current filters.",
    },
    "zh_cn": {
        "title": "银行营销分析看板",
        "subtitle": "历史营销效果分析与触达前客户认购倾向预测",
        "language": "语言",
        "filters": "筛选条件",
        "job": "职业",
        "channel": "联系渠道",
        "month": "月份",
        "all": "全部",
        "contacts": "营销联系量",
        "subscriptions": "认购数量",
        "conversion": "认购转化率",
        "attempts": "平均联系次数",
        "overview": "经营概览",
        "segments": "客户分群",
        "efficiency": "营销效率",
        "model": "模型与提升度",
        "priority": "优先名单",
        "monthly_title": "各月转化率与联系量",
        "channel_title": "各渠道转化率与联系量",
        "conversion_axis": "转化率",
        "volume_axis": "联系量",
        "month_axis": "月份",
        "channel_axis": "渠道",
        "job_title": "不同职业转化表现",
        "age_title": "不同年龄段转化表现",
        "job_axis": "职业",
        "age_axis": "年龄段",
        "sample_warning": "排名中已排除联系量少于 100 条的客群，避免小样本误导。",
        "attempt_title": "联系频次与转化率",
        "previous_title": "历史营销结果与本次转化",
        "attempt_axis": "联系强度",
        "previous_axis": "上次营销结果",
        "model_note": "模型排除了通话时长，因为该信息只有通话结束后才能获得。",
        "selected_model": "最终模型",
        "roc_auc": "ROC-AUC",
        "pr_auc": "PR-AUC",
        "recall": "召回率",
        "lift_title": "独立测试集累计收益曲线",
        "lift_x": "已联系客户占比",
        "lift_y": "累计覆盖认购客户占比",
        "model_curve": "模型排序",
        "random_curve": "随机触达",
        "decile_title": "各评分十分位转化率与提升度",
        "decile": "评分十分位",
        "response_rate": "转化率",
        "lift": "提升倍数",
        "importance_title": "主要模型信号",
        "importance": "相对重要性",
        "feature": "特征",
        "simulator": "营销容量模拟器",
        "simulator_help": "根据独立测试集的历史结果，估算按模型排序触达的表现。",
        "capacity": "计划联系客户数",
        "cost": "单次联系成本（估算）",
        "captured": "覆盖的历史认购客户",
        "capture_rate": "认购客户覆盖率",
        "target_conversion": "目标名单转化率",
        "cost_per_conversion": "每位认购客户的联系成本",
        "random_expected": "随机触达预计认购数",
        "contacts_avoided": "相比联系全部测试客户减少的联系量",
        "historical_only": "这是历史留出集模拟，不代表未来营销结果承诺。",
        "priority_segment": "优先级",
        "high": "高优先级",
        "medium": "中优先级",
        "low": "低优先级",
        "download": "下载筛选名单",
        "score": "认购倾向分数",
        "actual": "历史认购结果",
        "footer": "本项目使用 UCI Bank Marketing 公开数据。生成的客户编号对应营销记录，不代表经验证的唯一客户身份。",
        "no_data": "当前筛选条件下没有记录。",
    },
    "zh_tw": {
        "title": "銀行行銷分析看板",
        "subtitle": "歷史行銷成效分析與接觸前客戶認購傾向預測",
        "language": "語言",
        "filters": "篩選條件",
        "job": "職業",
        "channel": "聯絡渠道",
        "month": "月份",
        "all": "全部",
        "contacts": "行銷聯絡量",
        "subscriptions": "認購數量",
        "conversion": "認購轉換率",
        "attempts": "平均聯絡次數",
        "overview": "經營概覽",
        "segments": "客戶分群",
        "efficiency": "行銷效率",
        "model": "模型與提升度",
        "priority": "優先名單",
        "monthly_title": "各月轉換率與聯絡量",
        "channel_title": "各渠道轉換率與聯絡量",
        "conversion_axis": "轉換率",
        "volume_axis": "聯絡量",
        "month_axis": "月份",
        "channel_axis": "渠道",
        "job_title": "不同職業轉換表現",
        "age_title": "不同年齡層轉換表現",
        "job_axis": "職業",
        "age_axis": "年齡層",
        "sample_warning": "排名中已排除聯絡量少於 100 筆的客群，避免小樣本誤導。",
        "attempt_title": "聯絡頻率與轉換率",
        "previous_title": "歷史行銷結果與本次轉換",
        "attempt_axis": "聯絡強度",
        "previous_axis": "上次行銷結果",
        "model_note": "模型排除了通話時長，因為該資訊只有通話結束後才能取得。",
        "selected_model": "最終模型",
        "roc_auc": "ROC-AUC",
        "pr_auc": "PR-AUC",
        "recall": "召回率",
        "lift_title": "獨立測試集累計收益曲線",
        "lift_x": "已聯絡客戶占比",
        "lift_y": "累計涵蓋認購客戶占比",
        "model_curve": "模型排序",
        "random_curve": "隨機接觸",
        "decile_title": "各評分十分位轉換率與提升度",
        "decile": "評分十分位",
        "response_rate": "轉換率",
        "lift": "提升倍數",
        "importance_title": "主要模型訊號",
        "importance": "相對重要性",
        "feature": "特徵",
        "simulator": "行銷容量模擬器",
        "simulator_help": "根據獨立測試集的歷史結果，估算依模型排序接觸的表現。",
        "capacity": "計畫聯絡客戶數",
        "cost": "單次聯絡成本（估算）",
        "captured": "涵蓋的歷史認購客戶",
        "capture_rate": "認購客戶涵蓋率",
        "target_conversion": "目標名單轉換率",
        "cost_per_conversion": "每位認購客戶的聯絡成本",
        "random_expected": "隨機接觸預計認購數",
        "contacts_avoided": "相較聯絡全部測試客戶減少的聯絡量",
        "historical_only": "這是歷史留出集模擬，不代表未來行銷結果承諾。",
        "priority_segment": "優先級",
        "high": "高優先級",
        "medium": "中優先級",
        "low": "低優先級",
        "download": "下載篩選名單",
        "score": "認購傾向分數",
        "actual": "歷史認購結果",
        "footer": "本專案使用 UCI Bank Marketing 公開資料。產生的客戶編號對應行銷紀錄，不代表經驗證的唯一客戶身分。",
        "no_data": "目前篩選條件下沒有紀錄。",
    },
}

MONTH_LABELS = {
    "en": {},
    "zh_cn": {
        "Jan": "1月", "Feb": "2月", "Mar": "3月", "Apr": "4月",
        "May": "5月", "Jun": "6月", "Jul": "7月", "Aug": "8月",
        "Sep": "9月", "Oct": "10月", "Nov": "11月", "Dec": "12月",
    },
    "zh_tw": {
        "Jan": "1月", "Feb": "2月", "Mar": "3月", "Apr": "4月",
        "May": "5月", "Jun": "6月", "Jul": "7月", "Aug": "8月",
        "Sep": "9月", "Oct": "10月", "Nov": "11月", "Dec": "12月",
    },
}

VALUE_LABELS = {
    "en": {},
    "zh_cn": {
        "admin.": "行政", "blue-collar": "蓝领", "entrepreneur": "创业者",
        "housemaid": "家政", "management": "管理人员", "retired": "退休人员",
        "self-employed": "个体经营", "services": "服务业", "student": "学生",
        "technician": "技术人员", "unemployed": "待业", "unknown": "未知",
        "cellular": "手机", "telephone": "固定电话",
        "success": "成功", "failure": "失败", "other": "其他",
        "1 contact": "联系 1 次", "2 contacts": "联系 2 次",
        "3-4 contacts": "联系 3–4 次", "5+ contacts": "联系 5 次以上",
    },
    "zh_tw": {
        "admin.": "行政", "blue-collar": "藍領", "entrepreneur": "創業者",
        "housemaid": "家政", "management": "管理人員", "retired": "退休人員",
        "self-employed": "個體經營", "services": "服務業", "student": "學生",
        "technician": "技術人員", "unemployed": "待業", "unknown": "未知",
        "cellular": "手機", "telephone": "固定電話",
        "success": "成功", "failure": "失敗", "other": "其他",
        "1 contact": "聯絡 1 次", "2 contacts": "聯絡 2 次",
        "3-4 contacts": "聯絡 3–4 次", "5+ contacts": "聯絡 5 次以上",
    },
}

PRIORITY_RAW = ["High priority", "Medium priority", "Low priority"]
COLORS = {
    "primary": "#B34B3D",
    "blue": "#2F5597",
    "teal": "#2B7A78",
    "gold": "#B28704",
    "muted": "#D7DEE8",
}

st.set_page_config(page_title="Bank Marketing Analytics", layout="wide")


@st.cache_data
def load_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict,
]:
    return (
        pd.read_csv(DATA_FILE),
        pd.read_csv(SCORES_FILE),
        pd.read_csv(EVALUATION_FILE),
        pd.read_csv(IMPORTANCE_FILE),
        pd.read_csv(DECILE_FILE),
        json.loads(METRICS_FILE.read_text(encoding="utf-8")),
    )


def tr_value(value: str, locale: str) -> str:
    return VALUE_LABELS[locale].get(value, value)


def format_percentage_axis(fig: go.Figure) -> go.Figure:
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(
        margin=dict(l=10, r=10, t=55, b=10),
        legend_title_text="",
        hovermode="x unified",
    )
    return fig


df, scores, evaluation, importance, deciles, metrics = load_data()

query_locale = st.query_params.get("lang", "en")
language_names = list(LANGUAGES)
default_language_index = next(
    (
        index
        for index, language_name in enumerate(language_names)
        if LANGUAGES[language_name] == query_locale
    ),
    0,
)

with st.sidebar:
    selected_language = st.selectbox(
        "Language / 语言 / 語言",
        language_names,
        index=default_language_index,
    )
    locale = LANGUAGES[selected_language]
    if st.query_params.get("lang") != locale:
        st.query_params["lang"] = locale
    t = TEXT[locale]
    st.header(t["filters"])

    job_options = [t["all"]] + sorted(df["job"].unique().tolist())
    selected_job = st.selectbox(
        t["job"],
        job_options,
        format_func=lambda value: tr_value(value, locale),
    )
    channel_options = [t["all"]] + sorted(df["contact"].unique().tolist())
    selected_channel = st.selectbox(
        t["channel"],
        channel_options,
        format_func=lambda value: tr_value(value, locale),
    )
    month_values = (
        df.sort_values("month_number")["month_name"].drop_duplicates().tolist()
    )
    selected_month = st.selectbox(
        t["month"],
        [t["all"]] + month_values,
        format_func=lambda value: MONTH_LABELS[locale].get(value, value),
    )

filtered = df.copy()
if selected_job != t["all"]:
    filtered = filtered[filtered["job"] == selected_job]
if selected_channel != t["all"]:
    filtered = filtered[filtered["contact"] == selected_channel]
if selected_month != t["all"]:
    filtered = filtered[filtered["month_name"] == selected_month]

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2.5rem; max-width: 1420px;}
    [data-testid="stMetric"] {
        border-top: 3px solid #B34B3D;
        padding: 0.8rem 0.85rem 0.45rem;
        background: #F8F9FB;
    }
    [data-testid="stMetricLabel"] {font-weight: 600;}
    [data-testid="stSidebar"] {border-right: 1px solid #E2E5EA;}
    h1 {font-size: 2.35rem !important;}
    h2, h3 {letter-spacing: 0 !important;}
    [data-baseweb="tab-list"] {
        overflow-x: auto;
        scrollbar-width: thin;
    }
    [data-baseweb="tab"] {flex-shrink: 0;}
    @media (max-width: 640px) {
        .block-container {padding-top: 1rem; padding-left: 1rem; padding-right: 1rem;}
        h1 {font-size: 2rem !important;}
        [data-baseweb="tab"] {
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }
        [data-baseweb="tab"] p {font-size: 0.68rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(t["title"])
st.caption(t["subtitle"])

if filtered.empty:
    st.warning(t["no_data"])
    st.stop()

metric_columns = st.columns(4)
metric_columns[0].metric(t["contacts"], f"{len(filtered):,}")
metric_columns[1].metric(t["subscriptions"], f"{int(filtered['subscribed'].sum()):,}")
metric_columns[2].metric(t["conversion"], f"{filtered['subscribed'].mean():.1%}")
metric_columns[3].metric(t["attempts"], f"{filtered['campaign'].mean():.2f}")

overview_tab, segment_tab, efficiency_tab, model_tab, priority_tab = st.tabs(
    [t["overview"], t["segments"], t["efficiency"], t["model"], t["priority"]]
)

with overview_tab:
    left, right = st.columns(2)
    monthly = (
        filtered.groupby(["month_number", "month_name"], as_index=False)
        .agg(contacts=("contact_id", "count"), conversion=("subscribed", "mean"))
        .sort_values("month_number")
    )
    monthly["display_month"] = monthly["month_name"].map(
        lambda value: MONTH_LABELS[locale].get(value, value)
    )
    month_fig = px.line(
        monthly,
        x="display_month",
        y="conversion",
        markers=True,
        title=t["monthly_title"],
        labels={"display_month": t["month_axis"], "conversion": t["conversion_axis"]},
        custom_data=["contacts"],
        color_discrete_sequence=[COLORS["blue"]],
    )
    month_fig.update_traces(
        hovertemplate=(
            f"{t['month_axis']}: %{{x}}<br>"
            f"{t['conversion_axis']}: %{{y:.1%}}<br>"
            f"{t['volume_axis']}: %{{customdata[0]:,}}<extra></extra>"
        )
    )
    left.plotly_chart(format_percentage_axis(month_fig), use_container_width=True)

    channel = (
        filtered.groupby("contact", as_index=False)
        .agg(contacts=("contact_id", "count"), conversion=("subscribed", "mean"))
        .sort_values("conversion", ascending=False)
    )
    channel["display_channel"] = channel["contact"].map(
        lambda value: tr_value(value, locale)
    )
    channel_fig = px.bar(
        channel,
        x="display_channel",
        y="conversion",
        color="contacts",
        title=t["channel_title"],
        labels={
            "display_channel": t["channel_axis"],
            "conversion": t["conversion_axis"],
            "contacts": t["volume_axis"],
        },
        color_continuous_scale=["#DCE6F1", COLORS["blue"]],
    )
    right.plotly_chart(format_percentage_axis(channel_fig), use_container_width=True)

with segment_tab:
    st.caption(t["sample_warning"])
    left, right = st.columns(2)
    jobs = (
        filtered.groupby("job", as_index=False)
        .agg(contacts=("contact_id", "count"), conversion=("subscribed", "mean"))
        .query("contacts >= 100")
        .sort_values("conversion", ascending=True)
    )
    jobs["display_job"] = jobs["job"].map(lambda value: tr_value(value, locale))
    job_fig = px.bar(
        jobs,
        x="conversion",
        y="display_job",
        orientation="h",
        color="contacts",
        title=t["job_title"],
        labels={
            "conversion": t["conversion_axis"],
            "display_job": t["job_axis"],
            "contacts": t["volume_axis"],
        },
        color_continuous_scale=["#E6F2F1", COLORS["teal"]],
    )
    job_fig.update_xaxes(tickformat=".0%")
    job_fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    left.plotly_chart(job_fig, use_container_width=True)

    age = (
        filtered.groupby("age_band", as_index=False, observed=True)
        .agg(contacts=("contact_id", "count"), conversion=("subscribed", "mean"))
        .sort_values("age_band")
    )
    age_fig = px.bar(
        age,
        x="age_band",
        y="conversion",
        color="contacts",
        title=t["age_title"],
        labels={
            "age_band": t["age_axis"],
            "conversion": t["conversion_axis"],
            "contacts": t["volume_axis"],
        },
        color_continuous_scale=["#F1E8D1", COLORS["gold"]],
    )
    right.plotly_chart(format_percentage_axis(age_fig), use_container_width=True)

with efficiency_tab:
    left, right = st.columns(2)
    intensity_order = ["1 contact", "2 contacts", "3-4 contacts", "5+ contacts"]
    intensity = (
        filtered.groupby("campaign_intensity", as_index=False)
        .agg(contacts=("contact_id", "count"), conversion=("subscribed", "mean"))
    )
    intensity["campaign_intensity"] = pd.Categorical(
        intensity["campaign_intensity"], categories=intensity_order, ordered=True
    )
    intensity = intensity.sort_values("campaign_intensity")
    intensity["display_intensity"] = intensity["campaign_intensity"].astype(str).map(
        lambda value: tr_value(value, locale)
    )
    intensity_fig = px.bar(
        intensity,
        x="display_intensity",
        y="conversion",
        color="contacts",
        title=t["attempt_title"],
        labels={
            "display_intensity": t["attempt_axis"],
            "conversion": t["conversion_axis"],
            "contacts": t["volume_axis"],
        },
        color_continuous_scale=["#F7DFDA", COLORS["primary"]],
    )
    left.plotly_chart(format_percentage_axis(intensity_fig), use_container_width=True)

    previous = (
        filtered.groupby("poutcome", as_index=False)
        .agg(contacts=("contact_id", "count"), conversion=("subscribed", "mean"))
        .sort_values("conversion", ascending=False)
    )
    previous["display_outcome"] = previous["poutcome"].map(
        lambda value: tr_value(value, locale)
    )
    previous_fig = px.bar(
        previous,
        x="display_outcome",
        y="conversion",
        color="contacts",
        title=t["previous_title"],
        labels={
            "display_outcome": t["previous_axis"],
            "conversion": t["conversion_axis"],
            "contacts": t["volume_axis"],
        },
        color_continuous_scale=["#DCE6F1", COLORS["blue"]],
    )
    right.plotly_chart(format_percentage_axis(previous_fig), use_container_width=True)

with model_tab:
    st.info(t["model_note"])
    selected_metrics = next(
        row for row in metrics["models"] if row["model"] == metrics["selected_model"]
    )
    model_metrics = st.columns(4)
    model_metrics[0].metric(
        t["selected_model"], metrics["selected_model"].replace("_", " ").title()
    )
    model_metrics[1].metric(t["roc_auc"], f"{selected_metrics['roc_auc']:.3f}")
    model_metrics[2].metric(t["pr_auc"], f"{selected_metrics['pr_auc']:.3f}")
    model_metrics[3].metric(t["recall"], f"{selected_metrics['recall']:.1%}")

    left, right = st.columns(2)
    curve = evaluation.iloc[:: max(1, len(evaluation) // 250)].copy()
    curve = pd.concat([evaluation.iloc[[0]], curve, evaluation.iloc[[-1]]]).drop_duplicates(
        "rank"
    )
    lift_fig = go.Figure()
    lift_fig.add_trace(
        go.Scatter(
            x=curve["population_share"],
            y=curve["cumulative_capture_rate"],
            mode="lines",
            name=t["model_curve"],
            line=dict(color=COLORS["primary"], width=3),
        )
    )
    lift_fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name=t["random_curve"],
            line=dict(color="#8A9099", width=2, dash="dash"),
        )
    )
    lift_fig.update_layout(
        title=t["lift_title"],
        xaxis_title=t["lift_x"],
        yaxis_title=t["lift_y"],
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        margin=dict(l=10, r=10, t=55, b=10),
        legend_title_text="",
    )
    left.plotly_chart(lift_fig, use_container_width=True)

    decile_fig = go.Figure()
    decile_fig.add_trace(
        go.Bar(
            x=deciles["decile"],
            y=deciles["response_rate"],
            name=t["response_rate"],
            marker_color=COLORS["blue"],
        )
    )
    decile_fig.add_trace(
        go.Scatter(
            x=deciles["decile"],
            y=deciles["lift"],
            name=t["lift"],
            yaxis="y2",
            mode="lines+markers",
            line=dict(color=COLORS["primary"], width=3),
        )
    )
    decile_fig.update_layout(
        title=t["decile_title"],
        xaxis_title=t["decile"],
        yaxis=dict(title=t["response_rate"], tickformat=".0%"),
        yaxis2=dict(title=t["lift"], overlaying="y", side="right"),
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(orientation="h", y=-0.2),
    )
    right.plotly_chart(decile_fig, use_container_width=True)

    top_features = importance.head(15).sort_values("importance")
    importance_fig = px.bar(
        top_features,
        x="importance",
        y="feature",
        orientation="h",
        title=t["importance_title"],
        labels={"importance": t["importance"], "feature": t["feature"]},
        color_discrete_sequence=[COLORS["teal"]],
    )
    importance_fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(importance_fig, use_container_width=True)

    st.subheader(t["simulator"])
    st.caption(t["simulator_help"])
    control_left, control_right = st.columns([2, 1])
    capacity = control_left.slider(
        t["capacity"],
        min_value=max(100, len(evaluation) // 100),
        max_value=len(evaluation),
        value=max(100, len(evaluation) // 10),
        step=max(50, len(evaluation) // 100),
    )
    contact_cost = control_right.number_input(
        t["cost"], min_value=0.0, value=5.0, step=1.0
    )
    targeted = evaluation.head(capacity)
    captured = int(targeted["actual_subscribed"].sum())
    total_subscribers = int(evaluation["actual_subscribed"].sum())
    random_expected = capacity * float(evaluation["actual_subscribed"].mean())
    cost_per_conversion = (
        capacity * contact_cost / captured if captured else 0
    )
    simulator_metrics = st.columns(4)
    simulator_metrics[0].metric(t["captured"], f"{captured:,}")
    simulator_metrics[1].metric(
        t["capture_rate"], f"{captured / max(total_subscribers, 1):.1%}"
    )
    simulator_metrics[2].metric(
        t["target_conversion"], f"{captured / max(capacity, 1):.1%}"
    )
    simulator_metrics[3].metric(
        t["cost_per_conversion"], f"{cost_per_conversion:,.2f}"
    )
    st.write(
        f"**{t['random_expected']}:** {random_expected:,.1f}  ·  "
        f"**{t['contacts_avoided']}:** {len(evaluation) - capacity:,}"
    )
    st.caption(t["historical_only"])

with priority_tab:
    priority_labels = {
        "High priority": t["high"],
        "Medium priority": t["medium"],
        "Low priority": t["low"],
    }
    selected_priority_label = st.selectbox(
        t["priority_segment"],
        [priority_labels[value] for value in PRIORITY_RAW],
    )
    selected_priority = next(
        raw for raw, label in priority_labels.items() if label == selected_priority_label
    )
    display = (
        scores[scores["priority_segment"] == selected_priority]
        .sort_values("propensity_score", ascending=False)
        .head(1000)
        .copy()
    )
    display["job"] = display["job"].map(lambda value: tr_value(value, locale))
    display["contact"] = display["contact"].map(lambda value: tr_value(value, locale))
    display["month_name"] = display["month_name"].map(
        lambda value: MONTH_LABELS[locale].get(value, value)
    )
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "propensity_score": st.column_config.ProgressColumn(
                t["score"], min_value=0.0, max_value=1.0, format="%.3f"
            ),
            "subscribed": st.column_config.CheckboxColumn(t["actual"]),
        },
    )
    st.download_button(
        t["download"],
        display.to_csv(index=False).encode("utf-8-sig"),
        file_name="marketing_priority_list.csv",
        mime="text/csv",
    )

st.divider()
st.caption(t["footer"])
