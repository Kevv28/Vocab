import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date, timedelta

COLORS = {
    'primary': '#6C63FF',
    'secondary': '#FF6584',
    'success': '#43D9A2',
    'warning': '#FFB347',
    'bg': '#1E1E2E',
    'card': '#2A2A3E',
    'text': '#E0E0FF'
}

def weekly_progress_chart(stats):
    if not stats:
        return None
    dates = [str(s.date) for s in stats[-7:]]
    added = [s.words_added for s in stats[-7:]]
    revised = [s.words_revised for s in stats[-7:]]
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Added', x=dates, y=added, marker_color=COLORS['primary']))
    fig.add_trace(go.Bar(name='Revised', x=dates, y=revised, marker_color=COLORS['success']))
    fig.update_layout(
        barmode='group', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['text']),
        title='Weekly Progress', height=300, margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def monthly_chart(stats):
    if not stats:
        return None
    df = pd.DataFrame([{'date': str(s.date), 'words': s.words_added} for s in stats])
    fig = px.line(df, x='date', y='words', title='Monthly Learning',
                  color_discrete_sequence=[COLORS['primary']])
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def difficulty_pie(words):
    if not words:
        return None
    from collections import Counter
    counts = Counter(w.difficulty for w in words)
    fig = go.Figure(go.Pie(
        labels=list(counts.keys()), values=list(counts.values()),
        marker=dict(colors=[COLORS['success'], COLORS['warning'], COLORS['secondary']]),
        hole=0.4
    ))
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      title='Difficulty Distribution', height=280, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def streak_chart(stats):
    if not stats:
        return None
    dates = [str(s.date) for s in stats]
    active = [1 if (s.words_added > 0 or s.words_revised > 0) else 0 for s in stats]
    fig = go.Figure(go.Bar(x=dates, y=active, marker_color=[COLORS['success'] if a else COLORS['card'] for a in active]))
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', title='Study Streak', height=200,
                      margin=dict(l=20, r=20, t=40, b=20), yaxis=dict(showticklabels=False))
    return fig

def heatmap_chart(heatmap_data):
    today = date.today()
    start = today - timedelta(days=364)
    all_dates = []
    d = start
    while d <= today:
        all_dates.append(d)
        d += timedelta(days=1)

    weeks = []
    week = []
    for d in all_dates:
        week.append(d)
        if d.weekday() == 6:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)

    z, x, y = [], [], list('SMTWTFS')
    for week in weeks:
        col = []
        for dow in range(7):
            day = next((d for d in week if d.weekday() % 7 == (dow - 1) % 7), None)
            if day:
                col.append(heatmap_data.get(str(day), 0))
            else:
                col.append(None)
        z.append(col)
        x.append(week[0].strftime('%b %d') if week else '')

    fig = go.Figure(go.Heatmap(
        z=[[z[col][row] for col in range(len(z))] for row in range(7)],
        x=x, y=y,
        colorscale=[[0, COLORS['card']], [0.01, '#1a3a2a'], [0.5, '#2d6a4f'], [1, COLORS['success']]],
        showscale=False, xgap=2, ygap=2
    ))
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', height=160,
                      margin=dict(l=40, r=20, t=20, b=20), font=dict(size=10))
    return fig

def source_bar(words):
    if not words:
        return None
    from collections import Counter
    counts = Counter(w.source for w in words)
    fig = go.Figure(go.Bar(
        x=list(counts.keys()), y=list(counts.values()),
        marker_color=COLORS['primary']
    ))
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', title='Words by Source',
                      height=260, margin=dict(l=20, r=20, t=40, b=20))
    return fig
