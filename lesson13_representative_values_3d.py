"""틈새 공부 3D 수학 교실 ④: 평균·중앙값·최빈값의 차이.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly
실행: python -m streamlit run lesson13_representative_values_3d.py
"""

from collections import Counter


EXAMPLES = {
    "차이가 잘 보이는 자료": [3, 12, 2, 5, 3],
    "극단값이 없는 자료": [2, 3, 3, 4, 5],
    "자료가 짝수 개인 경우": [1, 2, 3, 7, 8, 9],
    "최빈값이 두 개인 자료": [1, 2, 2, 4, 4, 7],
    "최빈값이 없는 자료": [1, 2, 3, 4, 5],
}

STEP_TITLES = {
    1: "자료를 3D 기둥으로 세우기",
    2: "평균: 똑같이 나누기",
    3: "중앙값: 순서대로 줄 세우기",
    4: "최빈값: 가장 자주 나온 값 찾기",
    5: "세 대푯값의 차이 비교하기",
}


def format_number(value):
    value = float(value)
    if abs(value - round(value)) < 1e-9:
        return f"{value:.0f}"
    return f"{value:.1f}"


def representative_values(data):
    """평균·중앙값·최빈값을 교과서 정의에 따라 계산합니다."""
    if not data:
        raise ValueError("자료가 하나 이상 필요합니다.")

    numbers = [float(value) for value in data]
    ordered = sorted(numbers)
    count = len(ordered)
    mean = sum(ordered) / count

    middle = count // 2
    if count % 2:
        median = ordered[middle]
        middle_values = [ordered[middle]]
    else:
        middle_values = [ordered[middle - 1], ordered[middle]]
        median = sum(middle_values) / 2

    frequencies = Counter(ordered)
    highest_frequency = max(frequencies.values())
    modes = (
        sorted(value for value, frequency in frequencies.items()
               if frequency == highest_frequency)
        if highest_frequency > 1
        else []
    )

    return {
        "data": numbers,
        "ordered": ordered,
        "count": count,
        "sum": sum(ordered),
        "mean": mean,
        "median": median,
        "middle_values": middle_values,
        "frequencies": dict(sorted(frequencies.items())),
        "highest_frequency": highest_frequency,
        "modes": modes,
    }


def mode_text(modes):
    if not modes:
        return "없음"
    return ", ".join(format_number(value) for value in modes)


def centered_positions(count, gap=1.0):
    center = (count - 1) / 2
    return [(index - center) * gap for index in range(count)]


def scale_value(value, maximum, display_max=4.8):
    if maximum <= 0:
        return 0.0
    return float(value) / float(maximum) * display_max


def base_figure(title, front_view=False, height=345):
    import plotly.graph_objects as go

    eye = (
        dict(x=0.02, y=2.8, z=0.55)
        if front_view
        else dict(x=1.65, y=1.75, z=1.25)
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
            aspectratio=dict(x=1.38, y=0.72, z=1.22),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def fit_chart(figure, item_count, z_max=5.8):
    x_half = max(2.7, (item_count - 1) / 2 + 0.85)
    figure.update_layout(
        scene=dict(
            xaxis=dict(range=[-x_half, x_half], visible=False),
            yaxis=dict(range=[-1.35, 1.35], visible=False),
            zaxis=dict(range=[-0.65, z_max], visible=False),
        )
    )
    return figure


def cuboid_vertices(x_center, height, width=0.68, depth=0.72):
    x0, x1 = x_center - width / 2, x_center + width / 2
    y0, y1 = -depth / 2, depth / 2
    z0, z1 = 0, max(float(height), 0.04)
    return [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]


def add_bar(figure, x_center, display_height, label, color="#60A5FA", opacity=0.82):
    import plotly.graph_objects as go

    vertices = cuboid_vertices(x_center, display_height)
    i = [0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3]
    j = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4]
    k = [2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7]
    figure.add_trace(go.Mesh3d(
        x=[point[0] for point in vertices],
        y=[point[1] for point in vertices],
        z=[point[2] for point in vertices],
        i=i, j=j, k=k,
        color=color, opacity=opacity, flatshading=True,
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
        x=edge_x, y=edge_y, z=edge_z,
        mode="lines", line=dict(color="#1E3A8A", width=3),
        hoverinfo="skip",
    ))


def add_text(figure, point, text, color="#172554", size=14):
    import plotly.graph_objects as go

    figure.add_trace(go.Scatter3d(
        x=[point[0]], y=[point[1]], z=[point[2]],
        mode="text", text=[text],
        textfont=dict(color=color, size=size),
        hoverinfo="skip",
    ))


def add_line(figure, points, color="#F97316", width=5, dash=None, label="선"):
    import plotly.graph_objects as go

    figure.add_trace(go.Scatter3d(
        x=[point[0] for point in points],
        y=[point[1] for point in points],
        z=[point[2] for point in points],
        mode="lines", line=dict(color=color, width=width, dash=dash),
        hovertemplate=f"{label}<extra></extra>",
    ))


def add_mean_plane(figure, x_half, display_mean):
    import plotly.graph_objects as go

    points = [
        (-x_half, -0.62, display_mean), (x_half, -0.62, display_mean),
        (x_half, 0.62, display_mean), (-x_half, 0.62, display_mean),
    ]
    figure.add_trace(go.Mesh3d(
        x=[point[0] for point in points],
        y=[point[1] for point in points],
        z=[point[2] for point in points],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="#FBBF24", opacity=0.38, flatshading=True,
        hovertemplate="평균 높이<extra></extra>",
    ))
    add_line(
        figure,
        [(-x_half, -0.68, display_mean), (x_half, -0.68, display_mean)],
        "#EA580C", 7, None, "평균선",
    )


def data_bars_figure(data, step, front_view=False):
    stats = representative_values(data)
    shown = stats["ordered"] if step == 3 else stats["data"]
    maximum = max(stats["data"])
    positions = centered_positions(len(shown))
    figure = base_figure(f"{step}단계 · {STEP_TITLES[step]}", front_view)
    middle_indices = []
    if step == 3:
        middle = len(shown) // 2
        middle_indices = [middle] if len(shown) % 2 else [middle - 1, middle]

    for index, (x_position, value) in enumerate(zip(positions, shown)):
        display_height = scale_value(value, maximum)
        if step == 3 and index in middle_indices:
            color = "#FBBF24"
        elif step == 2 and value > stats["mean"]:
            color = "#F87171"
        elif step == 2 and value < stats["mean"]:
            color = "#60A5FA"
        else:
            color = "#93C5FD"
        add_bar(figure, x_position, display_height, f"자료값 {format_number(value)}", color)
        add_text(
            figure,
            (x_position, 0, display_height + 0.28),
            format_number(value),
            "#172554",
            15,
        )
        add_text(figure, (x_position, 0, -0.30), f"{index + 1}번", "#475569", 11)

    if step == 1:
        add_text(figure, (0, 0, 5.55), "기둥의 높이 = 자료값", "#1E3A8A", 15)
    elif step == 2:
        display_mean = scale_value(stats["mean"], maximum)
        x_half = max(abs(positions[0]), abs(positions[-1])) + 0.58
        add_mean_plane(figure, x_half, display_mean)
        add_text(
            figure,
            (0, -0.82, display_mean + 0.28),
            f"평균 = {format_number(stats['mean'])}",
            "#9A3412",
            15,
        )
        for x_position, value in zip(positions, shown):
            display_height = scale_value(value, maximum)
            color = "#DC2626" if value > stats["mean"] else "#0284C7"
            add_line(
                figure,
                [(x_position, 0.46, display_height), (x_position, 0.46, display_mean)],
                color, 4, "dot", "평균까지 옮길 양",
            )
    elif step == 3:
        if len(middle_indices) == 1:
            index = middle_indices[0]
            add_text(
                figure,
                (positions[index], -0.68, scale_value(shown[index], maximum) + 0.58),
                "가운데!",
                "#B45309",
                16,
            )
        else:
            first, second = middle_indices
            first_height = scale_value(shown[first], maximum)
            second_height = scale_value(shown[second], maximum)
            add_line(
                figure,
                [(positions[first], -0.62, first_height + 0.25),
                 (positions[second], -0.62, second_height + 0.25)],
                "#F59E0B", 6, None, "가운데 두 값",
            )
            add_text(figure, (0, -0.78, 5.45), "가운데 두 값의 평균", "#B45309", 15)
    return fit_chart(figure, len(shown))


def frequency_figure(data, front_view=False):
    stats = representative_values(data)
    items = list(stats["frequencies"].items())
    positions = centered_positions(len(items), gap=1.05)
    maximum_frequency = max(stats["frequencies"].values())
    figure = base_figure("4단계 · 같은 값끼리 모아 빈도 세기", front_view)

    for x_position, (value, frequency) in zip(positions, items):
        height = scale_value(frequency, maximum_frequency, 4.5)
        is_mode = frequency == maximum_frequency and maximum_frequency > 1
        color = "#FBBF24" if is_mode else "#93C5FD"
        add_bar(figure, x_position, height, f"값 {format_number(value)}: {frequency}번", color)
        add_text(figure, (x_position, 0, height + 0.28), f"{frequency}번", "#172554", 14)
        add_text(figure, (x_position, 0, -0.30), f"값 {format_number(value)}", "#475569", 11)
        if is_mode:
            add_text(figure, (x_position, -0.62, height + 0.62), "가장 자주!", "#B45309", 14)

    if not stats["modes"]:
        add_text(figure, (0, -0.65, 5.45), "모두 한 번씩 → 최빈값 없음", "#B91C1C", 15)
    return fit_chart(figure, len(items), z_max=5.75)


def comparison_figure(data, front_view=False):
    stats = representative_values(data)
    entries = [
        ("평균", stats["mean"], "#60A5FA"),
        ("중앙값", stats["median"], "#34D399"),
    ]
    if stats["modes"]:
        entries.extend(("최빈값", value, "#FBBF24") for value in stats["modes"])
    else:
        entries.append(("최빈값 없음", 0.0, "#CBD5E1"))

    maximum = max([value for _, value, _ in entries] + [1.0])
    positions = centered_positions(len(entries), gap=1.18)
    figure = base_figure("5단계 · 세 대푯값을 나란히 비교", front_view)

    for x_position, (name, value, color) in zip(positions, entries):
        if value > 0:
            display_height = scale_value(value, maximum, 4.6)
            add_bar(figure, x_position, display_height, f"{name} {format_number(value)}", color, 0.86)
            add_text(figure, (x_position, 0, display_height + 0.30), format_number(value), "#172554", 15)
        else:
            display_height = 0.15
            add_bar(figure, x_position, display_height, name, color, 0.65)
            add_text(figure, (x_position, 0, 0.48), "없음", "#B91C1C", 14)
        add_text(figure, (x_position, 0, -0.32), name, "#334155", 11)

    if stats["mean"] > stats["median"] and max(stats["data"]) >= stats["mean"] * 2:
        add_text(figure, (0, -0.70, 5.45), "큰 값 하나가 평균을 위로 끌어올려요", "#B91C1C", 14)
    return fit_chart(figure, len(entries), z_max=5.75)


def make_figure(data, step, front_view=False):
    if step in (1, 2, 3):
        return data_bars_figure(data, step, front_view)
    if step == 4:
        return frequency_figure(data, front_view)
    if step == 5:
        return comparison_figure(data, front_view)
    raise ValueError("설명 단계는 1부터 5까지입니다.")


def mean_formula(stats):
    joined = "+".join(format_number(value) for value in stats["data"])
    return (
        rf"\text{{평균}}=\frac{{{joined}}}{{{stats['count']}}}"
        rf"=\frac{{{format_number(stats['sum'])}}}{{{stats['count']}}}"
        rf"={format_number(stats['mean'])}"
    )


def median_formula(stats):
    ordered = r",\;".join(format_number(value) for value in stats["ordered"])
    if stats["count"] % 2:
        calculation = format_number(stats["median"])
    else:
        first, second = stats["middle_values"]
        calculation = (
            rf"\frac{{{format_number(first)}+{format_number(second)}}}{{2}}"
            rf"={format_number(stats['median'])}"
        )
    return rf"{ordered}\quad\Rightarrow\quad\text{{중앙값}}={calculation}"


def frequency_formula(stats):
    parts = [
        rf"{format_number(value)}\text{{은(는) }}{frequency}\text{{번}}"
        for value, frequency in stats["frequencies"].items()
    ]
    return r",\quad ".join(parts)


def lesson_content(data, step):
    stats = representative_values(data)
    if step == 1:
        explanation = (
            "자료 하나를 기둥 하나로 바꾸었습니다. 기둥이 높을수록 값이 큽니다. "
            "아직 순서가 뒤섞여 있어도 평균은 계산할 수 있어요."
        )
        key = "대푯값은 자료 전체의 특징을 하나의 값으로 나타낸 수입니다."
        formula = None
    elif step == 2:
        explanation = (
            "모든 기둥의 양을 한곳에 모은 뒤 사람 수만큼 똑같이 나눠 봅니다. "
            "높은 기둥이 낮은 기둥에게 나누어 주어 모두 같은 높이가 된 값이 평균입니다."
        )
        key = "평균은 모든 자료값을 사용하므로 아주 큰 값이나 작은 값의 영향을 받습니다."
        formula = mean_formula(stats)
    elif step == 3:
        if stats["count"] % 2:
            middle_message = "자료가 홀수 개라서 한가운데 값이 중앙값입니다."
        else:
            middle_message = "자료가 짝수 개라서 가운데 두 값의 평균이 중앙값입니다."
        explanation = (
            "자료를 작은 값부터 큰 값까지 차례대로 줄 세웁니다. "
            + middle_message
        )
        key = "중앙값은 순서만 보므로 극단적으로 큰 값의 영향을 적게 받습니다."
        formula = median_formula(stats)
    elif step == 4:
        if stats["modes"]:
            mode_message = f"가장 많이 나온 {mode_text(stats['modes'])}이(가) 최빈값입니다."
        else:
            mode_message = "모든 값이 한 번씩만 나와 최빈값이 없습니다."
        explanation = (
            "같은 값끼리 모아서 몇 번 나왔는지 세어 봅니다. "
            + mode_message
        )
        key = "최빈값은 없을 수도 있고, 두 개 이상일 수도 있습니다."
        formula = frequency_formula(stats)
    elif step == 5:
        explanation = (
            "평균은 모든 값을 똑같이 나눈 값, 중앙값은 순서의 가운데 값, "
            "최빈값은 가장 자주 나온 값입니다. 자료의 모습에 따라 알맞은 대푯값을 골라야 합니다."
        )
        key = "평균·중앙값·최빈값은 같을 수도 있고 서로 다를 수도 있습니다."
        formula = None
    else:
        raise ValueError("설명 단계는 1부터 5까지입니다.")
    return {
        "title": f"{step}. {STEP_TITLES[step]}",
        "explanation": explanation,
        "key": key,
        "formula": formula,
        "stats": stats,
    }


def show_step_card(st, data, step):
    content = lesson_content(data, step)
    stats = content["stats"]
    st.progress(step / 5)
    st.markdown(f"### {content['title']}")
    st.info(content["explanation"])
    if content["formula"]:
        st.latex(content["formula"])
    if step == 5:
        first, second, third = st.columns(3)
        first.metric("평균", format_number(stats["mean"]))
        second.metric("중앙값", format_number(stats["median"]))
        third.metric("최빈값", mode_text(stats["modes"]))
    st.success(f"⭐ {content['key']}")


def main():
    import streamlit as st

    st.set_page_config(
        page_title="틈새 공부 3D 대푯값 교실",
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
    [data-testid="stMetricValue"] {font-size: 1.55rem;}
    @media (max-width: 640px) {
        .block-container {padding: 0.35rem 0.48rem 0.85rem;}
        h1 {font-size: 1.32rem !important;}
        h2 {font-size: 1.03rem !important;}
        h3 {font-size: 0.96rem !important;}
        p, label, [data-testid="stCaptionContainer"] {font-size: 0.86rem !important;}
        [data-testid="stAlert"] {font-size: 0.84rem; padding: 0.52rem 0.62rem;}
        [data-testid="stMetricValue"] {font-size: 1.25rem;}
        .stButton button {min-height: 2.1rem; padding: 0.2rem 0.35rem;}
        [data-testid="stPlotlyChart"] {max-width: 100% !important; overflow: hidden;}
    }
</style>
""", unsafe_allow_html=True)

    st.title("📊 틈새 공부 3D 수학 교실")
    st.subheader("④ 자료와 가능성 · 대푯값")
    st.caption(
        "평균·중앙값·최빈값의 차이가 5장면으로 자동 재생됩니다. "
        "멈추고 싶을 때 ‘일시정지’를 누르세요."
    )

    example_label = st.selectbox("살펴볼 예시 자료", list(EXAMPLES))
    data = EXAMPLES[example_label]
    st.markdown("**현재 자료:**　" + "　".join(format_number(value) for value in data))

    if "representative_step" not in st.session_state:
        st.session_state.representative_step = 1
    if st.session_state.get("representative_last_example") != example_label:
        st.session_state.representative_step = 1
        st.session_state.representative_last_example = example_label

    first_control, second_control = st.columns(2)
    with first_control:
        paused = st.toggle("⏸ 일시정지", value=False)
    with second_control:
        front_view = st.checkbox("▥ 정면에서 비교", value=False)

    speed = st.slider(
        "장면 전환 시간(초)", 2.0, 7.0, 3.5, 0.5,
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
        step = st.session_state.representative_step

        if paused:
            previous, replay, next_scene = st.columns(3)
            if previous.button("◀ 이전", use_container_width=True):
                step = 5 if step == 1 else step - 1
                st.session_state.representative_step = step
            if replay.button("↺ 처음", use_container_width=True):
                step = 1
                st.session_state.representative_step = step
            if next_scene.button("다음 ▶", use_container_width=True):
                step = 1 if step == 5 else step + 1
                st.session_state.representative_step = step

        state_text = "멈춘 상태 · 버튼으로 장면 이동" if paused else f"{speed:g}초마다 자동 재생 중"
        st.markdown(f"**현재 {step}/5장면** · {state_text}")
        show_step_card(st, data, step)

        figure = make_figure(data, step, front_view)
        st.plotly_chart(
            figure,
            use_container_width=True,
            config={"displaylogo": False, "displayModeBar": False, "responsive": True},
        )
        st.caption("☝️ 한 손가락으로 회전 · 두 손가락으로 확대/축소")

        if supports_auto and not paused:
            st.session_state.representative_step = 1 if step == 5 else step + 1

    show_simulation()

    with st.expander("🧠 평균·중앙값·최빈값을 한눈에 보기"):
        st.markdown("""
| 대푯값 | 찾는 방법 | 알맞은 경우 | 꼭 조심할 점 |
|---|---|---|---|
| **평균** | 합계 ÷ 자료 수 | 전체 값을 모두 반영할 때 | 극단값의 영향을 많이 받음 |
| **중앙값** | 순서대로 놓은 가운데 값 | 극단값이 있을 때 | 짝수 개면 가운데 두 값의 평균 |
| **최빈값** | 가장 자주 나온 값 | 가장 흔한 값을 찾을 때 | 없거나 여러 개일 수 있음 |

**기억법:** 평균은 **나누기**, 중앙값은 **줄 세우기**, 최빈값은 **횟수 세기**입니다.
""")


if __name__ == "__main__":
    main()
