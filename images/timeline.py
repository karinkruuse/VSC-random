import matplotlib.pyplot as plt
from adjustText import adjust_text

events = {
    1916: "Einstein predicts\nGWs",
    1965: "first Weber bar",
    1979: "LIGO funding approved",
    1992: "LISA proposed",
    2002: "LIGO first data",
    2015: "First detection\n(GW150914)",
    2035: "LISA launch"
}

years = list(events.keys())

fig, ax = plt.subplots(figsize=(12, 3))
ax.hlines(1, min(years)-5, max(years)+5, color='black')
ax.plot(years, [1]*len(years), "o", color="#667982")

# Add labels with rectangular boxes and larger offsets
texts = []
offset = 0.15
for i, (year, label) in enumerate(events.items()):
    y_pos = 1 + offset if i % 2 == 0 else 1 - offset  # farther from the line
    va = 'bottom' if i % 2 == 0 else 'top'
    t = ax.text(year, y_pos, f"{year}\n{label}",
                ha='center',
                va=va,
                fontsize=12,
                fontname="Arial",
                color="#667982",
                bbox=dict(facecolor='white', edgecolor="#667982", boxstyle='square,pad=0.3'))  # rectangular box
    texts.append(t)

# Adjust texts slightly to avoid overlap
#adjust_text(texts, only_move={'points':'y', 'text':'y'}, arrowprops=None)

# Arrow for current year
ax.annotate("2025", 
            xy=(2025, 1), xytext=(2025, 1.25),  # also offset arrow text more
            arrowprops=dict(facecolor="#667982", edgecolor="#667982", shrink=0.05, width=0.9, headwidth=8),
            ha='center', va='bottom',
            fontsize=12, fontname="Arial", color="#667982")

# Clean up axes
ax.set_ylim(0.75, 1.4)  # make room for higher text
ax.set_xticks([])
ax.set_yticks([])
ax.axis("off")

plt.savefig("timeline.png", dpi=400, bbox_inches='tight')
plt.show()
