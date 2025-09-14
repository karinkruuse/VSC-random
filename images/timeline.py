import matplotlib.pyplot as plt

# Timeline events with year and labels
events = {
    1916: "Einstein predicts\nGWs",
    1965: "first Weber bar",
    1990: "LIGO funding approved                             ",
    1992: "LISA proposed",
    2002: "LIGO first data",
    2015: "First detection\n(GW150914)",
    2035: "LISA launch"
}


years = list(events.keys())

# Plot timeline
fig, ax = plt.subplots(figsize=(12, 3))

# Draw main line
ax.hlines(1, min(years)-5, max(years)+5, color='black')

# Add event points
ax.plot(years, [1]*len(years), "o", color="#667982")

# Add labels
for i, (year, label) in enumerate(events.items()):
    ax.text(year, 1.05 if i % 2 == 0 else 0.95, f"{year}\n{label}",
            ha='center',
            va='bottom' if i % 2 == 0 else 'top',
            fontsize=10,
            fontname="Arial",
            color="#667982")

# Add arrow for current year (2025)
ax.annotate("2025", 
            xy=(2025, 1), xytext=(2025, 1.15),
            arrowprops=dict(facecolor="#667982", shrink=0.05, width=1, headwidth=8),
            ha='center', va='bottom',
            fontsize=10, fontname="Arial", color="#667982")

# Clean up axes
ax.set_ylim(0.75, 1.25)
ax.set_xticks([])
ax.set_yticks([])
ax.axis("off")

plt.show()