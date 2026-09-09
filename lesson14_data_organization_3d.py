"""틈새 공부 3D 수학 교실 ⑤: 자료의 정리.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly
실행: python -m streamlit run lesson14_data_organization_3d.py
"""

from collections import OrderedDict


EXAMPLES = OrderedDict({
    "수학 점수 자료": [24, 12, 37, 22, 31, 17, 42, 28, 22, 34, 14, 25],
    "하루 독서 쪽수": [18, 35, 21, 16, 29, 41, 24, 32, 27, 45, 36, 12],
    "줄넘기 성공 횟수": [33, 21, 47, 26, 38, 42, 29, 35, 51, 24, 44, 31],
    "달리기 기록 자료": [14, 18, 22, 16, 25, 31, 27, 19, 24, 33, 28, 21],
})

STEP_TITLES = {
    1: "흩어진 원자료 살펴보기",
    2: "작은 값부터 줄 세우고 자릿값 나누기",
    3: "줄기와 잎 그림 완성하기",
    4: "계급을 만들고 도수 세기",
    5: "도수를 히스토그램으로 나타내기",
}


def format_number(value):
    value = float(value)
    if abs(value - round(value)) < 1e-9:
        return f"{value:.0f}"
    return f"{value:.1f}"


def organize_data(data, class_width=10):
    """두 자리 자연수 자료를 줄기·잎과 도수분포로 정리합니다."""
    if not data:
        raise ValueError("자료가 하나 이상 필요합니다.")
    if class_width <= 0:
        raise ValueError("계급의 크기는 양수여야 합니다.")

    numbers = [int(value) for value in data]
    if any(value < 0 or value >= 100 for value in numbers):
        raise ValueError("이 수업에서는 0 이상 100 미만의 정수를 사용합니다.")

    ordered = sorted(numbers)
    stem_leaf = OrderedDict()
    for value in ordered:
        stem, leaf = divmod(value, 10)
        stem_leaf.setdefault(stem, []).append(leaf)

    first_boundary = (min(ordered) // class_width) * class_width
    last_boundary = ((max(ordered) // class_width) + 1) * class_width
    classes = []
    for lower in range(first_boundary, last_boundary, class_width):
        upper_exclusive = lower + class_width
        frequency = sum(lower <= value < upper_exclusive for value in ordered)
        classes.append({
            "lower": lower,
            "upper_exclusive": upper_exclusive,
            "upper_inclusive": upper_exclusive - 1,
            "frequency": frequency,
        })

    return {
        "data": numbers,
        "ordered": ordered,
        "count": len(numbers),
        "stem_leaf": stem_leaf,
        "class_width": class_width,
        "classes": classes,
        "frequency_sum": sum(item["frequency"] for item in classes),
    }


def centered_positions(count, gap=1.0):
    center = (count - 1) / 2
    return [(index - center) * gap for index in range(count)]


def scale_value(value, maximum, display_max=4.6):
    if maximum <= 0:
        return 0.0
    return float(value) / float(maximum) * display_max


def base_figure(title, front_view=False, height=345, aspect=None):
    import plotly.graph_objects as go

    eye = (
        dict(x=0.02, y=2.9, z=0.65)
        if front_view
        else dict(x=1.6, y=1.8, z=1.28)
    )
    figure = go.Figure()
    figure.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=15)),
        height=height,
        margin=dict(l=0, r=0, t=38, b=0),
        showlegend=False,
        scene=dict(
            camera=dict(eye=eye, projection=dict(type="orthographic")),
            aspectmode="manual",
            aspectratio=aspect or dict(x=1.42, y=0.72, z=1.16),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def fit_chart(figure, x_range, y_range=(-1.4, 1.4), z_range=(-0.65, 5.8)):
    figure.update_layout(scene=dict(
        xaxis=dict(range=list(x_range), visible=False),
        yaxis=dict(range=list(y_range), visible=False),
        zaxis=dict(range=list(z_range), visible=False),
    ))
    return figure


def box_vertices(x_center, y_center, z_base, width, depth, height):
    x0, x1 = x_center - width / 2, x_center + width / 2
    y0, y1 = y_center - depth / 2, y_center + depth / 2
    z0, z1 = z_base, z_base + max(float(height), 0.035)
    return [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]


def add_box(
    figure,
    x_center,
    y_center,
    height,
    label,
    color="#60A5FA",
    width=0.68,
    depth=0.72,
    z_base=0,
    opacity=0.84,
    edge_color="#1E3A8A",
):
    import plotly.graph_objects as go

    vertices = box_vertices(x_center, y_center, z_base, width, depth, height)
    i = [0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3]
    j = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4]
    k = [2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7]
    figure.add_trace(go.Mesh3d(
        x=[point[0] for point in vertices],
        y=[point[1] for point in vertices],
        z=[point[2] for point in vertices],
        i=i,
        j=j,
        k=k,
        color=color,
        opacity=opacity,
        flatshading=True,
        hovertemplate=f"{label}<extra></extra>",
    ))

    edge_pairs = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    edge_x, edge_y, edge_z = [], [], []
    for first, second in edge_pairs:
        edge_x.extend([vertices[first][0], vertices[second][0], None])
        edge_y.extend([vertices[first][1], vertices[second][1], None])
        edge_z.extend([vertices[first][2], vertices[second][2], None])
    figure.add_trace(go.Scatter3d(
        x=edge_x,
        y=edge_y,
        z=edge_z,
        mode="lines",
        line=dict(color=edge_color, width=3),
        hoverinfo="skip",
    ))


def add_text(figure, point, text, color="#172554", size=14):
    import plotly.graph_objects as go

    figure.add_trace(go.Scatter3d(
        x=[point[0]],
        y=[point[1]],
        z=[point[2]],
        mode="text",
        text=[text],
        textfont=dict(color=color, size=size),
        hoverinfo="skip",
    ))


def add_line(figure, points, color="#F97316", width=5, dash=None, label="선"):
    import plotly.graph_objects as go

    figure.add_trace(go.Scatter3d(
        x=[point[0] for point in points],
        y=[point[1] for point in points],
        z=[point[2] for point in points],
        mode="lines",
        line=dict(color=color, width=width, dash=dash),
        hovertemplate=f"{label}<extra></extra>",
    ))


def raw_data_figure(data, front_view=False):
    stats = organize_data(data)
    maximum = max(stats["data"])
    positions = centered_positions(stats["count"], gap=0.62)
    figure = base_figure("1단계 · 원자료는 아직 순서가 뒤섞여 있어요", front_view)

    for index, (x_position, value) in enumerate(zip(positions, stats["data"])):
        display_height = scale_value(value, maximum)
        add_box(
            figure,
            x_position,
            0,
            display_height,
            f"{index + 1}번째 자료: {value}",
            color="#93C5FD",
            width=0.48,
            depth=0.64,
        )
        add_text(figure, (x_position, 0, display_height + 0.23), str(value), size=12)
    add_text(figure, (0, -0.82, 5.40), "값 하나 = 기둥 하나", "#1D4ED8", 15)
    half = max(3.75, abs(positions[-1]) + 0.45)
    return fit_chart(figure, (-half, half), z_range=(-0.30, 5.75))


def sorted_figure(data, front_view=False):
    stats = organize_data(data)
    maximum = max(stats["ordered"])
    positions = centered_positions(stats["count"], gap=0.62)
    figure = base_figure("2단계 · 작은 값부터 줄 세워요", front_view)

    for x_position, value in zip(positions, stats["ordered"]):
        display_height = scale_value(value, maximum)
        stem, leaf = divmod(value, 10)
        add_box(
            figure,
            x_position,
            0,
            display_height,
            f"{value} = 줄기 {stem}, 잎 {leaf}",
            color="#86EFAC" if value != stats["ordered"][4] else "#FBBF24",
            width=0.48,
            depth=0.64,
        )
        add_text(figure, (x_position, 0, display_height + 0.22), str(value), size=12)

    example = stats["ordered"][4]
    stem, leaf = divmod(example, 10)
    add_text(
        figure,
        (0, -0.86, 5.40),
        f"{example} = 줄기 {stem} | 잎 {leaf}",
        "#9A3412",
        16,
    )
    half = max(3.75, abs(positions[-1]) + 0.45)
    return fit_chart(figure, (-half, half), z_range=(-0.30, 5.75))


def stem_leaf_figure(data, front_view=False):
    stats = organize_data(data)
    rows = list(stats["stem_leaf"].items())
    max_leaves = max(len(leaves) for _, leaves in rows)
    figure = base_figure(
        "3단계 · 줄기는 한 번, 잎은 빠짐없이 써요",
        front_view,
        aspect=dict(x=1.48, y=0.82, z=0.62),
    )

    row_positions = centered_positions(len(rows), gap=1.05)
    for y_position, (stem, leaves) in zip(reversed(row_positions), rows):
        add_box(
            figure,
            -3.0,
            y_position,
            0.38,
            f"줄기 {stem}",
            color="#FBBF24",
            width=0.72,
            depth=0.72,
            opacity=0.90,
            edge_color="#B45309",
        )
        add_text(figure, (-3.0, y_position, 0.62), str(stem), "#713F12", 16)
        for index, leaf in enumerate(leaves):
            x_position = -1.95 + index * 0.82
            add_box(
                figure,
                x_position,
                y_position,
                0.32,
                f"줄기 {stem}, 잎 {leaf} → {stem * 10 + leaf}",
                color="#93C5FD",
                width=0.66,
                depth=0.68,
                opacity=0.88,
            )
            add_text(figure, (x_position, y_position, 0.52), str(leaf), "#172554", 15)

    y_half = max(2.0, abs(row_positions[0]) + 0.65)
    x_right = max(2.65, -1.95 + (max_leaves - 1) * 0.82 + 0.55)
    add_line(
        figure,
        [(-2.55, -y_half, 0.02), (-2.55, y_half, 0.02)],
        "#EA580C",
        7,
        None,
        "줄기와 잎을 나누는 선",
    )
    add_text(figure, (-3.0, -y_half - 0.20, 0.10), "줄기", "#92400E", 13)
    add_text(figure, (-1.35, -y_half - 0.20, 0.10), "잎", "#1E3A8A", 13)
    return fit_chart(
        figure,
        (-3.75, x_right),
        y_range=(-y_half - 0.35, y_half + 0.35),
        z_range=(-0.10, 1.45),
    )


def frequency_figure(data, front_view=False):
    stats = organize_data(data)
    classes = stats["classes"]
    positions = centered_positions(len(classes), gap=1.35)
    maximum_frequency = max(item["frequency"] for item in classes)
    figure = base_figure("4단계 · 같은 계급에 든 자료를 세어요", front_view)

    for x_position, item in zip(positions, classes):
        frequency = item["frequency"]
        for level in range(frequency):
            add_box(
                figure,
                x_position,
                0,
                0.66,
                (
                    f"{item['lower']} 이상 {item['upper_exclusive']} 미만: "
                    f"{frequency}개"
                ),
                color="#93C5FD" if level < frequency - 1 else "#60A5FA",
                width=0.88,
                depth=0.76,
                z_base=level * 0.68,
                opacity=0.88,
            )
        top = max(frequency * 0.68, 0.12)
        add_text(figure, (x_position, 0, top + 0.26), f"도수 {frequency}", "#172554", 14)
        add_text(
            figure,
            (x_position, 0, -0.34),
            f"{item['lower']}~{item['upper_inclusive']}",
            "#475569",
            11,
        )

    add_text(
        figure,
        (0, -0.82, maximum_frequency * 0.68 + 0.82),
        f"도수의 합 = {stats['frequency_sum']} (전체 자료 수)",
        "#1D4ED8",
        14,
    )
    half = max(2.8, abs(positions[-1]) + 0.85)
    return fit_chart(
        figure,
        (-half, half),
        z_range=(-0.60, max(4.9, maximum_frequency * 0.68 + 1.30)),
    )


def histogram_figure(data, front_view=False):
    stats = organize_data(data)
    classes = stats["classes"]
    positions = centered_positions(len(classes), gap=1.0)
    maximum_frequency = max(item["frequency"] for item in classes)
    figure = base_figure("5단계 · 도수만큼 높이고 막대는 서로 붙여요", front_view)

    for x_position, item in zip(positions, classes):
        display_height = scale_value(item["frequency"], maximum_frequency, 4.45)
        add_box(
            figure,
            x_position,
            0,
            display_height,
            (
                f"{item['lower']} 이상 {item['upper_exclusive']} 미만: "
                f"도수 {item['frequency']}"
            ),
            color="#60A5FA",
            width=1.0,
            depth=0.82,
            opacity=0.82,
            edge_color="#1D4ED8",
        )
        add_text(
            figure,
            (x_position, 0, display_height + 0.27),
            str(item["frequency"]),
            "#172554",
            15,
        )
        add_text(
            figure,
            (x_position, 0, -0.35),
            f"{item['lower']}~{item['upper_inclusive']}",
            "#334155",
            11,
        )

    left_edge = positions[0] - 0.5
    right_edge = positions[-1] + 0.5
    add_line(
        figure,
        [(left_edge, -0.54, 0), (right_edge, -0.54, 0)],
        "#0F172A",
        6,
        None,
        "가로축",
    )
    add_text(figure, (0, -0.91, 5.35), "빈틈 없음 = 연속된 계급", "#9A3412", 15)
    half = max(2.75, abs(positions[-1]) + 0.72)
    return fit_chart(figure, (-half, half), z_range=(-0.62, 5.75))


def make_figure(data, step, front_view=False):
    if step == 1:
        return raw_data_figure(data, front_view)
    if step == 2:
        return sorted_figure(data, front_view)
    if step == 3:
        return stem_leaf_figure(data, front_view)
    if step == 4:
        return frequency_figure(data, front_view)
    if step == 5:
        return histogram_figure(data, front_view)
    raise ValueError("설명 단계는 1부터 5까지입니다.")


def stem_leaf_text(stats):
    lines = []
    for stem, leaves in stats["stem_leaf"].items():
        lines.append(f"**{stem}**　│　" + "　".join(str(leaf) for leaf in leaves))
    return "  \n".join(lines)


def frequency_table_text(stats):
    rows = ["| 계급 | 도수 |", "|---|---:|"]
    for item in stats["classes"]:
        rows.append(
            f"| {item['lower']} 이상 {item['upper_exclusive']} 미만 | "
            f"{item['frequency']} |"
        )
    rows.append(f"| **합계** | **{stats['frequency_sum']}** |")
    return "\n".join(rows)


def lesson_content(data, step):
    stats = organize_data(data)
    if step == 1:
        explanation = (
            "조사해서 처음 얻은 값을 원자료라고 합니다. 값이 뒤섞여 있으면 "
            "전체 모습을 한눈에 보기 어려우므로 일정한 방법으로 정리해야 합니다."
        )
        key = "자료를 정리하면 값이 어디에 많이 모였는지 쉽게 볼 수 있습니다."
        detail = None
    elif step == 2:
        example = stats["ordered"][4]
        stem, leaf = divmod(example, 10)
        explanation = (
            "먼저 자료를 작은 값부터 차례대로 놓습니다. 두 자리 수에서는 십의 자리를 "
            f"줄기, 일의 자리를 잎으로 나눕니다. 예를 들어 {example}의 줄기는 {stem}, "
            f"잎은 {leaf}입니다."
        )
        key = "줄기는 십의 자리, 잎은 일의 자리입니다."
        detail = "정렬:　" + "　".join(str(value) for value in stats["ordered"])
    elif step == 3:
        explanation = (
            "같은 줄기를 가진 수를 한 줄에 모으고, 잎을 작은 수부터 씁니다. "
            "원래 자료값을 모두 남기므로 개별 값도 다시 읽을 수 있습니다."
        )
        key = "줄기 2 옆의 잎 4는 24를 뜻합니다. 줄기와 잎 사이에는 세로선을 긋습니다."
        detail = stem_leaf_text(stats)
    elif step == 4:
        explanation = (
            "자료가 들어갈 범위를 계급이라고 하고, 계급의 간격을 계급의 크기라고 합니다. "
            "각 계급에 들어간 자료의 개수가 도수입니다."
        )
        key = (
            f"이 표의 계급 크기는 {stats['class_width']}이고, 도수의 합 "
            f"{stats['frequency_sum']}은 전체 자료 수와 같습니다."
        )
        detail = frequency_table_text(stats)
    elif step == 5:
        explanation = (
            "도수분포표의 계급을 가로축에 놓고, 도수만큼 직사각형의 높이를 올립니다. "
            "계급이 끊기지 않고 이어지므로 히스토그램의 직사각형도 서로 붙입니다."
        )
        key = "히스토그램은 자료가 어느 구간에 많이 모였는지 모양으로 보여 줍니다."
        detail = None
    else:
        raise ValueError("설명 단계는 1부터 5까지입니다.")
    return {
        "title": f"{step}. {STEP_TITLES[step]}",
        "explanation": explanation,
        "key": key,
        "detail": detail,
        "stats": stats,
    }


def show_step_card(st, data, step):
    content = lesson_content(data, step)
    st.progress(step / 5)
    st.markdown(f"### {content['title']}")
    st.info(content["explanation"])
    if content["detail"]:
        st.markdown(content["detail"])
    st.success(f"⭐ {content['key']}")


def main():
    import streamlit as st

    st.set_page_config(
        page_title="틈새 공부 3D 자료 정리 교실",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown("""
<style>
    .block-container {max-width: 720px; padding-top: 0.65rem; padding-bottom: 1rem;}
    h1 {font-size: 1.72rem !important; line-height: 1.2 !important; margin-bottom: 0.15rem !important;}
    h2 {font-size: 1.24rem !important;}
    h3 {font-size: 1.06rem !important;}
    [data-testid="stAlert"] {padding: 0.65rem 0.8rem;}
    @media (max-width: 640px) {
        .block-container {padding: 0.35rem 0.48rem 0.85rem;}
        h1 {font-size: 1.32rem !important;}
        h2 {font-size: 1.03rem !important;}
        h3 {font-size: 0.96rem !important;}
        p, label, [data-testid="stCaptionContainer"] {font-size: 0.86rem !important;}
        [data-testid="stAlert"] {font-size: 0.84rem; padding: 0.52rem 0.62rem;}
        .stButton button {min-height: 2.1rem; padding: 0.2rem 0.35rem;}
        [data-testid="stPlotlyChart"] {max-width: 100% !important; overflow: hidden;}
        table {font-size: 0.82rem !important;}
    }
</style>
""", unsafe_allow_html=True)

    st.title("📊 틈새 공부 3D 수학 교실")
    st.subheader("⑤ 자료와 가능성 · 자료의 정리")
    st.caption(
        "원자료가 줄기와 잎 그림·도수분포표·히스토그램으로 바뀌는 과정이 "
        "5장면으로 자동 재생됩니다."
    )

    example_label = st.selectbox("살펴볼 예시 자료", list(EXAMPLES))
    data = EXAMPLES[example_label]
    st.markdown("**현재 자료:**　" + "　".join(str(value) for value in data))

    if "organization_step" not in st.session_state:
        st.session_state.organization_step = 1
    if st.session_state.get("organization_last_example") != example_label:
        st.session_state.organization_step = 1
        st.session_state.organization_last_example = example_label

    first_control, second_control = st.columns(2)
    with first_control:
        paused = st.toggle("⏸ 일시정지", value=False)
    with second_control:
        front_view = st.checkbox("▥ 정면에서 보기", value=False)

    speed = st.slider(
        "장면 전환 시간(초)",
        2.0,
        7.0,
        3.5,
        0.5,
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
        step = st.session_state.organization_step

        if paused:
            previous, replay, next_scene = st.columns(3)
            if previous.button("◀ 이전", width="stretch"):
                step = 5 if step == 1 else step - 1
                st.session_state.organization_step = step
            if replay.button("↺ 처음", width="stretch"):
                step = 1
                st.session_state.organization_step = step
            if next_scene.button("다음 ▶", width="stretch"):
                step = 1 if step == 5 else step + 1
                st.session_state.organization_step = step

        state_text = "멈춘 상태 · 버튼으로 장면 이동" if paused else f"{speed:g}초마다 자동 재생 중"
        st.markdown(f"**현재 {step}/5장면** · {state_text}")
        show_step_card(st, data, step)

        figure = make_figure(data, step, front_view)
        st.plotly_chart(
            figure,
            width="stretch",
            config={"displaylogo": False, "displayModeBar": False, "responsive": True},
        )
        st.caption("☝️ 한 손가락으로 회전 · 두 손가락으로 확대/축소")

        if supports_auto and not paused:
            st.session_state.organization_step = 1 if step == 5 else step + 1

    show_simulation()

    with st.expander("🧠 세 가지 자료 정리 방법을 한눈에 보기"):
        st.markdown("""
| 정리 방법 | 무엇을 보여 주나요? | 꼭 기억할 점 |
|---|---|---|
| **줄기와 잎 그림** | 개별 자료값과 전체 분포 | 잎은 작은 수부터 씀 |
| **도수분포표** | 각 계급에 들어간 자료의 수 | 도수의 합 = 전체 자료 수 |
| **히스토그램** | 계급별 도수를 그림으로 비교 | 계급이 이어져 막대도 서로 붙음 |

**기억법:** 줄기와 잎은 **자릿값 나누기**, 도수분포표는 **구간별로 세기**,
히스토그램은 **도수만큼 높이기**입니다.
""")


if __name__ == "__main__":
    main()
