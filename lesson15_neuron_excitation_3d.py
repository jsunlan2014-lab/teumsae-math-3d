"""틈새 공부 3D 생명과학 교실 ①: 뉴런에서 흥분이 전도되는 과정.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly
실행: python -m streamlit run lesson15_neuron_excitation_3d.py

이 시뮬레이션은 고등학교 생명과학 수준의 개념 모형입니다.
막전위 값은 대표값이며 실제 뉴런과 조건에 따라 달라질 수 있습니다.
"""

from math import cos, pi, sin


TOTAL_STEPS = 7
SEGMENT_NAMES = ("A", "B", "C", "D", "E")
SEGMENT_X = (-3.6, -1.8, 0.0, 1.8, 3.6)

STEP_TITLES = {
    1: "휴지 전위: 출발 준비",
    2: "역치 도달: 활동 전위 시작",
    3: "Na⁺ 유입: 빠른 탈분극",
    4: "이웃 구간으로 국소 전류 이동",
    5: "K⁺ 유출: 재분극과 불응기",
    6: "같은 크기로 한 방향 전도",
    7: "휴지 상태 회복과 핵심 정리",
}

STATE_STYLE = {
    "휴지": ("#93C5FD", "#1D4ED8"),
    "역치": ("#FDE68A", "#B45309"),
    "탈분극": ("#FB7185", "#BE123C"),
    "재분극": ("#C4B5FD", "#6D28D9"),
    "불응기": ("#CBD5E1", "#475569"),
}


def step_model(step):
    """각 장면의 축삭 구간 상태와 설명을 반환합니다."""
    models = {
        1: {
            "states": ["휴지", "휴지", "휴지", "휴지", "휴지"],
            "potentials": [-70, -70, -70, -70, -70],
            "na_in": [],
            "k_out": [],
            "current": None,
            "explanation": (
                "자극을 받기 전에는 세포 안이 바깥보다 음(-)전하를 띱니다. "
                "K⁺ 누출 통로와 Na⁺/K⁺ 펌프가 이온 농도 차를 유지합니다."
            ),
            "key": "휴지 전위는 보통 약 −70 mV입니다.",
        },
        2: {
            "states": ["역치", "휴지", "휴지", "휴지", "휴지"],
            "potentials": [-55, -70, -70, -70, -70],
            "na_in": [],
            "k_out": [],
            "current": None,
            "explanation": (
                "충분한 자극을 받은 A 구간의 막전위가 역치에 도달합니다. "
                "역치에 이르면 전압 개폐성 Na⁺ 통로가 빠르게 열리기 시작합니다."
            ),
            "key": "역치 미만이면 활동 전위가 생기지 않습니다.",
        },
        3: {
            "states": ["탈분극", "역치", "휴지", "휴지", "휴지"],
            "potentials": [30, -55, -70, -70, -70],
            "na_in": [0],
            "k_out": [],
            "current": (0, 1),
            "explanation": (
                "전압 개폐성 Na⁺ 통로가 열려 Na⁺이 세포 안으로 들어옵니다. "
                "A 구간의 막전위는 빠르게 상승하고, 생긴 국소 전류가 B 구간을 자극합니다."
            ),
            "key": "Na⁺ 유입 → 탈분극 → 막전위 상승",
        },
        4: {
            "states": ["재분극", "탈분극", "역치", "휴지", "휴지"],
            "potentials": [-20, 30, -55, -70, -70],
            "na_in": [1],
            "k_out": [0],
            "current": (1, 2),
            "explanation": (
                "B 구간에서는 Na⁺이 유입되어 새로운 활동 전위가 생깁니다. "
                "A 구간에서는 Na⁺ 통로가 불활성화되고 K⁺ 통로가 열려 재분극이 시작됩니다."
            ),
            "key": "앞에서는 탈분극, 바로 뒤에서는 재분극이 일어납니다.",
        },
        5: {
            "states": ["불응기", "재분극", "탈분극", "역치", "휴지"],
            "potentials": [-80, -20, 30, -55, -70],
            "na_in": [2],
            "k_out": [1],
            "current": (2, 3),
            "explanation": (
                "흥분은 C 구간에서 다시 만들어집니다. 지나온 A·B 구간은 재분극 또는 "
                "불응기이므로 곧바로 다시 흥분하기 어렵습니다."
            ),
            "key": "K⁺ 유출이 재분극을 만들고, 불응기가 역방향 전도를 막습니다.",
        },
        6: {
            "states": ["휴지", "불응기", "재분극", "탈분극", "역치"],
            "potentials": [-70, -80, -20, 30, -55],
            "na_in": [3],
            "k_out": [2],
            "current": (3, 4),
            "explanation": (
                "각 구간에서 활동 전위가 새롭게 발생하므로 흥분은 축삭 끝을 향해 이동합니다. "
                "활동 전위의 크기는 이동하면서 작아지지 않습니다."
            ),
            "key": "흥분 전도: 활동 전위가 이웃 구간에서 연속적으로 재생성되는 과정",
        },
        7: {
            "states": ["휴지", "휴지", "휴지", "휴지", "휴지"],
            "potentials": [-70, -70, -70, -70, -70],
            "na_in": [],
            "k_out": [],
            "current": None,
            "explanation": (
                "K⁺ 통로가 닫히고 막전위가 휴지 수준으로 돌아옵니다. Na⁺/K⁺ 펌프는 "
                "ATP를 사용하여 장기적으로 Na⁺·K⁺ 농도 차를 유지합니다."
            ),
            "key": "Na⁺ 유입 → 탈분극 / K⁺ 유출 → 재분극 / 불응기 → 한 방향 전도",
        },
    }
    if step not in models:
        raise ValueError("설명 단계는 1부터 7까지입니다.")
    return models[step]


def cylinder_surface(x_center, length=1.42, radius=0.78, resolution=28):
    """x축 방향의 짧은 원통 표면 좌표를 만듭니다."""
    angles = [2 * pi * index / (resolution - 1) for index in range(resolution)]
    x0, x1 = x_center - length / 2, x_center + length / 2
    x = [[x0 for _ in angles], [x1 for _ in angles]]
    y = [[radius * cos(angle) for angle in angles] for _ in range(2)]
    z = [[radius * sin(angle) for angle in angles] for _ in range(2)]
    return x, y, z


def add_membrane_segment(figure, x_center, state, name, potential):
    import plotly.graph_objects as go

    fill_color, edge_color = STATE_STYLE[state]
    x, y, z = cylinder_surface(x_center)
    figure.add_trace(go.Surface(
        x=x,
        y=y,
        z=z,
        surfacecolor=[[0] * len(x[0]), [0] * len(x[0])],
        colorscale=[[0, fill_color], [1, fill_color]],
        cmin=0,
        cmax=1,
        opacity=0.58,
        showscale=False,
        hovertemplate=(
            f"{name} 구간<br>{state}<br>막전위 {potential:+d} mV<extra></extra>"
        ),
    ))

    angles = [2 * pi * index / 36 for index in range(37)]
    for ring_x in (x_center - 0.71, x_center + 0.71):
        figure.add_trace(go.Scatter3d(
            x=[ring_x] * len(angles),
            y=[0.78 * cos(angle) for angle in angles],
            z=[0.78 * sin(angle) for angle in angles],
            mode="lines",
            line=dict(color=edge_color, width=4),
            hoverinfo="skip",
        ))

    figure.add_trace(go.Scatter3d(
        x=[x_center, x_center],
        y=[0, 0],
        z=[1.16, -1.12],
        mode="text",
        text=[f"<b>{name} · {state}</b>", f"{potential:+d} mV"],
        textfont=dict(color="#172554", size=13),
        hoverinfo="skip",
    ))


def add_ion_clouds(figure):
    """막 바깥의 Na⁺와 막 안의 K⁺ 분포를 간단히 보여 줍니다."""
    import plotly.graph_objects as go

    sodium_x, sodium_y, sodium_z = [], [], []
    potassium_x, potassium_y, potassium_z = [], [], []
    offsets = (-0.34, 0.0, 0.34)
    for center in SEGMENT_X:
        for offset in offsets:
            sodium_x.append(center + offset)
            sodium_y.append(0.08)
            sodium_z.append(1.48 + 0.10 * abs(offset))
        for offset in (-0.30, 0.30):
            potassium_x.append(center + offset)
            potassium_y.append(0.0)
            potassium_z.append(0.15 if offset < 0 else -0.18)

    figure.add_trace(go.Scatter3d(
        x=sodium_x,
        y=sodium_y,
        z=sodium_z,
        mode="markers",
        marker=dict(size=5, color="#F97316", symbol="circle"),
        hovertemplate="막 바깥에 많은 Na⁺<extra></extra>",
    ))
    figure.add_trace(go.Scatter3d(
        x=potassium_x,
        y=potassium_y,
        z=potassium_z,
        mode="markers",
        marker=dict(size=5, color="#7C3AED", symbol="diamond"),
        hovertemplate="막 안에 많은 K⁺<extra></extra>",
    ))


def add_ion_arrow(figure, segment_index, ion, inward=True):
    import plotly.graph_objects as go

    x_center = SEGMENT_X[segment_index]
    if inward:
        start_z, end_z = 1.70, 0.38
        color = "#EA580C"
        label = "Na⁺ 유입"
    else:
        start_z, end_z = 0.32, 1.66
        color = "#6D28D9"
        label = "K⁺ 유출"

    figure.add_trace(go.Scatter3d(
        x=[x_center, x_center],
        y=[-0.12, -0.12],
        z=[start_z, end_z],
        mode="lines+text",
        line=dict(color=color, width=9),
        text=[ion, ""],
        textposition="top center",
        textfont=dict(color=color, size=14),
        hovertemplate=f"{label}<extra></extra>",
    ))
    figure.add_trace(go.Cone(
        x=[x_center],
        y=[-0.12],
        z=[end_z],
        u=[0],
        v=[0],
        w=[-0.38 if inward else 0.38],
        anchor="tip",
        sizemode="absolute",
        sizeref=0.25,
        colorscale=[[0, color], [1, color]],
        showscale=False,
        hoverinfo="skip",
    ))


def add_local_current(figure, first_index, second_index):
    import plotly.graph_objects as go

    x0 = SEGMENT_X[first_index] + 0.45
    x1 = SEGMENT_X[second_index] - 0.40
    figure.add_trace(go.Scatter3d(
        x=[x0, x1],
        y=[-0.93, -0.93],
        z=[0.18, 0.18],
        mode="lines+text",
        line=dict(color="#DC2626", width=9),
        text=["", "국소 전류 →"],
        textposition="top center",
        textfont=dict(color="#B91C1C", size=13),
        hovertemplate="국소 전류가 다음 구간을 역치까지 탈분극시킵니다.<extra></extra>",
    ))
    figure.add_trace(go.Cone(
        x=[x1],
        y=[-0.93],
        z=[0.18],
        u=[0.35],
        v=[0],
        w=[0],
        anchor="tip",
        sizemode="absolute",
        sizeref=0.25,
        colorscale=[[0, "#DC2626"], [1, "#DC2626"]],
        showscale=False,
        hoverinfo="skip",
    ))


def make_figure(step, front_view=False, height=375):
    import plotly.graph_objects as go

    model = step_model(step)
    figure = go.Figure()
    add_ion_clouds(figure)

    for index, (center, name, state, potential) in enumerate(zip(
        SEGMENT_X,
        SEGMENT_NAMES,
        model["states"],
        model["potentials"],
    )):
        add_membrane_segment(figure, center, state, name, potential)

    for index in model["na_in"]:
        add_ion_arrow(figure, index, "Na⁺", inward=True)
    for index in model["k_out"]:
        add_ion_arrow(figure, index, "K⁺", inward=False)
    if model["current"]:
        add_local_current(figure, *model["current"])

    figure.add_trace(go.Scatter3d(
        x=[-4.35, 4.40],
        y=[0.93, 0.93],
        z=[2.05, 2.05],
        mode="lines+text",
        line=dict(color="#2563EB", width=6),
        text=["", "흥분 진행 방향 →"],
        textposition="top center",
        textfont=dict(color="#1D4ED8", size=14),
        hoverinfo="skip",
    ))

    eye = (
        dict(x=0.01, y=3.55, z=0.45)
        if front_view
        else dict(x=1.15, y=2.25, z=1.18)
    )
    figure.update_layout(
        title=dict(
            text=f"{step}단계 · {STEP_TITLES[step]}",
            x=0.5,
            xanchor="center",
            font=dict(size=15, color="#172554"),
        ),
        height=height,
        margin=dict(l=0, r=0, t=42, b=0),
        showlegend=False,
        scene=dict(
            camera=dict(eye=eye, projection=dict(type="orthographic")),
            aspectmode="manual",
            aspectratio=dict(x=2.25, y=0.78, z=1.02),
            xaxis=dict(range=[-4.75, 4.85], visible=False),
            yaxis=dict(range=[-1.30, 1.30], visible=False),
            zaxis=dict(range=[-1.45, 2.45], visible=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#172554"),
    )
    return figure


def short_explanation(step):
    model = step_model(step)
    return model["explanation"], model["key"]


def main():
    import streamlit as st

    st.set_page_config(
        page_title="틈새 공부 3D 생명과학 · 뉴런의 흥분 전도",
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    if "neuron_shorts_mode" not in st.session_state:
        st.session_state.neuron_shorts_mode = True
    if "neuron_step" not in st.session_state:
        st.session_state.neuron_step = 1

    shorts_mode = st.session_state.neuron_shorts_mode

    st.markdown("""
<style>
    .block-container {max-width: 760px; padding-top: 0.65rem; padding-bottom: 1rem;}
    h1 {font-size: 1.70rem !important; line-height: 1.18 !important; margin-bottom: 0.15rem !important;}
    h2 {font-size: 1.22rem !important;}
    h3 {font-size: 1.03rem !important;}
    [data-testid="stAlert"] {padding: 0.62rem 0.78rem;}
    [data-testid="stPlotlyChart"] {max-width: 100% !important; overflow: hidden;}
    @media (max-width: 640px) {
        .block-container {padding: 0.30rem 0.42rem 0.75rem;}
        h1 {font-size: 1.28rem !important;}
        h2 {font-size: 1.02rem !important;}
        h3 {font-size: 0.94rem !important;}
        p, label, [data-testid="stCaptionContainer"] {font-size: 0.84rem !important;}
        [data-testid="stAlert"] {font-size: 0.82rem; padding: 0.48rem 0.58rem;}
        .stButton button {min-height: 2.10rem; padding: 0.18rem 0.30rem;}
    }
</style>
""", unsafe_allow_html=True)

    if shorts_mode:
        st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], #MainMenu, footer {display: none !important;}
    .block-container {max-width: 430px; padding: 0.16rem 0.34rem 0.34rem !important;}
    [data-testid="stVerticalBlock"] {gap: 0.30rem !important;}
    [data-testid="stProgressBar"] {margin: 0 !important;}
    .bio-brand {
        color: #172554; font-size: 1.18rem; font-weight: 800;
        line-height: 1.15; text-align: center; margin: 0.05rem 0 0.02rem;
    }
    .bio-topic {
        color: #1D4ED8; font-size: 0.92rem; font-weight: 750;
        text-align: center; margin-bottom: 0.08rem;
    }
    .bio-step {
        color: #172554; font-size: 0.99rem; font-weight: 800;
        text-align: center; line-height: 1.18; margin: 0.02rem 0 0.16rem;
    }
    .bio-explanation {
        background: #E8F2FF; color: #174A7C; border-radius: 0.58rem;
        padding: 0.46rem 0.58rem; font-size: 0.82rem; font-weight: 600;
        line-height: 1.40; margin-bottom: 0;
    }
    .bio-key {
        background: #E7F8EE; color: #166534; border-radius: 0.58rem;
        padding: 0.46rem 0.58rem; font-size: 0.84rem; font-weight: 750;
        line-height: 1.34; text-align: center; margin-top: -0.08rem;
    }
    [data-testid="stPlotlyChart"] {height: 375px !important; overflow: hidden;}
    [data-testid="stPlotlyChart"] > div {height: 375px !important;}
    [data-testid="stToggle"] {margin: 0 !important;}
    div[data-testid="stButton"] button {min-height: 1.95rem !important;}
</style>
<div class="bio-brand">🧠 틈새 공부 3D 생명과학</div>
<div class="bio-topic">뉴런에서 흥분이 전도되는 과정</div>
""", unsafe_allow_html=True)
        paused = st.toggle("⏸ 화면 멈춤", value=False, key="neuron_paused")
        speed = 3.8
        front_view = False
    else:
        st.title("🧠 틈새 공부 3D 생명과학 교실")
        st.subheader("① 뉴런에서 흥분이 전도되는 과정")
        st.caption(
            "막전위 변화와 Na⁺·K⁺ 이동이 축삭의 이웃 구간으로 이어지는 과정을 "
            "7장면으로 살펴봅니다. 그림은 손가락으로 회전·확대할 수 있습니다."
        )
        first, second = st.columns(2)
        with first:
            paused = st.toggle("⏸ 일시정지", value=False, key="neuron_paused_full")
        with second:
            front_view = st.checkbox("▥ 정면에서 보기", value=False)
        speed = st.slider(
            "장면 전환 시간(초)",
            2.0,
            7.0,
            3.8,
            0.2,
            disabled=paused,
        )

    supports_auto = hasattr(st, "fragment")
    if not supports_auto:
        st.warning(
            "자동 재생에는 Streamlit 1.37 이상이 필요합니다. 터미널에서 "
            "`python -m pip install --upgrade streamlit`을 실행해 주세요."
        )
    run_interval = f"{speed}s" if supports_auto and not paused else None
    decorator = st.fragment(run_every=run_interval) if supports_auto else (lambda function: function)

    @decorator
    def show_simulation():
        step = int(st.session_state.neuron_step)

        if paused:
            previous, replay, next_scene = st.columns(3)
            if previous.button("◀ 이전", width="stretch", key="neuron_previous"):
                step = TOTAL_STEPS if step == 1 else step - 1
                st.session_state.neuron_step = step
            if replay.button("↺ 처음", width="stretch", key="neuron_replay"):
                step = 1
                st.session_state.neuron_step = step
            if next_scene.button("다음 ▶", width="stretch", key="neuron_next"):
                step = 1 if step == TOTAL_STEPS else step + 1
                st.session_state.neuron_step = step

        model = step_model(step)
        st.progress(step / TOTAL_STEPS)

        if shorts_mode:
            st.markdown(
                f"""
<div class="bio-step">{step}/{TOTAL_STEPS}　{STEP_TITLES[step]}</div>
<div class="bio-explanation">{model['explanation']}</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"### {step}. {STEP_TITLES[step]}")
            st.info(model["explanation"])

        figure = make_figure(step, front_view=front_view, height=375 if shorts_mode else 470)
        st.plotly_chart(
            figure,
            width="stretch",
            config={
                "displayModeBar": False,
                "scrollZoom": True,
                "responsive": True,
            },
        )

        if shorts_mode:
            st.markdown(
                f'<div class="bio-key">⭐ {model["key"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.success(f"⭐ {model['key']}")

        if supports_auto and not paused:
            st.session_state.neuron_step = 1 if step == TOTAL_STEPS else step + 1

    show_simulation()

    if shorts_mode:
        with st.expander("🧠 수능 핵심과 전체 수업 보기"):
            st.markdown(
                """
- **탈분극:** 전압 개폐성 Na⁺ 통로가 열리고 Na⁺이 유입됩니다.
- **재분극:** Na⁺ 통로가 불활성화되고 K⁺ 통로가 열려 K⁺이 유출됩니다.
- **불응기:** 지나온 구간이 즉시 다시 흥분하지 못해 전도가 주로 한 방향으로 일어납니다.
- **Na⁺/K⁺ 펌프:** 재분극을 직접 만드는 주역이 아니라 이온 농도 차를 장기적으로 유지합니다.
"""
            )
            if st.button("넓은 수업 화면으로 전환", width="stretch"):
                st.session_state.neuron_shorts_mode = False
                st.rerun()
    else:
        with st.expander("📌 색과 기호 읽는 법", expanded=False):
            st.markdown(
                """
| 표시 | 뜻 |
|---|---|
| 주황색 원·화살표 | 막 바깥에 많은 Na⁺와 Na⁺ 유입 |
| 보라색 마름모·화살표 | 막 안에 많은 K⁺와 K⁺ 유출 |
| 붉은 화살표 | 다음 축삭 구간으로 퍼지는 국소 전류 |
| 회색 구간 | 흥분 직후 다시 흥분하기 어려운 불응기 |
"""
            )
        st.warning(
            "이 그림은 개념 이해를 위한 단순화 모형입니다. 실제 막전위와 이온 통로의 "
            "작동 시간은 뉴런의 종류와 환경에 따라 달라질 수 있습니다."
        )
        if st.button("📱 Shorts 한 화면으로 돌아가기", width="stretch"):
            st.session_state.neuron_shorts_mode = True
            st.rerun()


if __name__ == "__main__":
    main()
