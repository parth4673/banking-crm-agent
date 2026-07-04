"""Generate architecture diagram as PNG using matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(16, 11))
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis('off')
fig.patch.set_facecolor('white')

ui_color = '#E3F2FD'
agent_color = '#FFF3E0'
tools_color = '#E8F5E9'
db_color = '#F3E5F5'
border_ui = '#1565C0'
border_agent = '#E65100'
border_tools = '#2E7D32'
border_db = '#6A1B9A'

ui_box = mpatches.FancyBboxPatch((0.5, 9.2), 15, 1.3, boxstyle="round,pad=0.15",
                                   facecolor=ui_color, edgecolor=border_ui, linewidth=2)
ax.add_patch(ui_box)
ax.text(8, 10.2, '🖥️  STREAMLIT CHAT UI', fontsize=14, fontweight='bold',
        ha='center', color=border_ui)
ax.text(4, 9.65, 'RM types query', fontsize=10, ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#90CAF9'))
ax.text(8, 9.65, 'Chat Interface', fontsize=10, ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#90CAF9'))
ax.text(12, 9.65, 'Real-time Status', fontsize=10, ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#90CAF9'))

ax.annotate('', xy=(8, 8.6), xytext=(8, 9.15),
            arrowprops=dict(arrowstyle='->', color='#333', lw=2))

agent_box = mpatches.FancyBboxPatch((0.5, 5.8), 15, 2.8, boxstyle="round,pad=0.15",
                                     facecolor=agent_color, edgecolor=border_agent, linewidth=2)
ax.add_patch(agent_box)
ax.text(8, 8.2, '🧠  AGENT LOOP (with retry & validation)', fontsize=14,
        fontweight='bold', ha='center', color=border_agent)

boxes = [
    (2.5, 7.2, 'Conversation\nHistory'),
    (6, 7.2, 'LLM\n(Groq/OpenAI/Gemini)'),
    (10, 7.2, 'Tool Calls?'),
    (13.5, 7.2, 'Return\nFinal Answer'),
    (8, 6.2, 'Validate\nInputs'),
    (11.5, 6.2, 'Execute\nTool'),
    (4.5, 6.2, 'Feed Results\nBack to LLM'),
]
for (x, y, text) in boxes:
    ax.text(x, y, text, fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#FFB74D'))

arrows = [
    ((3.5, 7.2), (5, 7.2)),
    ((7.2, 7.2), (9, 7.2)),
    ((11, 7.2), (12.5, 7.2)),
    ((10, 6.9), (10, 6.55)),
    ((9, 6.2), (10.5, 6.2)),
    ((8, 5.95), (5.5, 6.0)),
    ((4.5, 6.55), (4.5, 7.0)),
]
for (start, end) in arrows:
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.5))

ax.text(10.5, 7.55, 'No', fontsize=8, color='green', fontweight='bold')
ax.text(10.2, 6.7, 'Yes', fontsize=8, color='red', fontweight='bold')

ax.annotate('', xy=(8, 5.15), xytext=(8, 5.75),
            arrowprops=dict(arrowstyle='->', color='#333', lw=2))

tools_box = mpatches.FancyBboxPatch((0.5, 3.2), 15, 1.9, boxstyle="round,pad=0.15",
                                     facecolor=tools_color, edgecolor=border_tools, linewidth=2)
ax.add_patch(tools_box)
ax.text(8, 4.75, '🔧  TOOLS LAYER (7 tools)', fontsize=14, fontweight='bold',
        ha='center', color=border_tools)

tool_names = [
    'get_high_value\n_customers', 'get_customer\n_profile', 'search\n_customers',
    'score_conversion\n_likelihood', 'recommend\n_products', 'get_product\n_catalog',
    'generate_whatsapp\n_message'
]
for i, name in enumerate(tool_names):
    x = 1.5 + i * 2
    ax.text(x, 3.85, name, fontsize=7, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='#81C784'))

ax.annotate('', xy=(8, 2.6), xytext=(8, 3.15),
            arrowprops=dict(arrowstyle='->', color='#333', lw=2))

db_box = mpatches.FancyBboxPatch((0.5, 0.5), 15, 2.0, boxstyle="round,pad=0.15",
                                  facecolor=db_color, edgecolor=border_db, linewidth=2)
ax.add_patch(db_box)
ax.text(8, 2.15, '💾  SQLite DATABASE', fontsize=14, fontweight='bold',
        ha='center', color=border_db)

tables = ['customers\n(50)', 'transactions\n(~1300)', 'products\n(8)',
          'customer_products\n(~100)', 'interaction_log\n(~125)']
for i, name in enumerate(tables):
    x = 2 + i * 2.8
    ax.text(x, 1.15, name, fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#CE93D8'))

plt.tight_layout()
plt.savefig('assets/architecture.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✅ Architecture diagram saved to assets/architecture.png")
