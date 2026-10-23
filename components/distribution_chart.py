import plotly.graph_objects as go
from typing import Dict

def render_measurement_chart(probabilities: Dict[str, float]):
    """Renders an interactive probability distribution bar chart."""
    sorted_items = sorted(probabilities.items(), key=lambda x: int(x[0], 2))
    bitstrings = [item[0] for item in sorted_items]
    probs = [item[1] for item in sorted_items]

    fig = go.Figure(data=[
        go.Bar(
            x=bitstrings,
            y=probs,
            marker_color="#00D2FF",
            text=[f"{p:.3f}" for p in probs],
            textposition="auto"
        )
    ])
    fig.update_layout(
        title="Measurement Probability Distribution |Counting Register⟩",
        xaxis_title="Basis State (Binary / Phase Bin)",
        yaxis_title="Probability",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    return fig