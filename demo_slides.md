# Demo Slides: AI Agents for Data Analysis Platform

## Slide 1: Title & Overview
**AI Agents for Data Analysis and Visualization**

- **What It Is**: A Streamlit app that uses two AI agents to analyze data and create visualizations automatically.
- **Why It Matters**: Makes data analysis accessible – users ask questions in plain English, get insights and charts instantly.
- **Tech Stack**: Python, Streamlit (UI), LangChain (AI), OpenAI GPT (LLMs), SQLite (data).
- **Demo Goal**: Show how agents work together for fast, accurate BI.

---

## Slide 2: System Structure
**How the Platform is Built**

- **Frontend (UI)**: Streamlit app – user selects DB, types query, sees results.
- **Agents (Core Logic)**:
  - Analysis Agent: Reads DB schema, runs SQL, summarizes data.
  - Visualization Agent: Generates Python code for charts (Matplotlib/Seaborn).
- **Workflow**: LangGraph connects agents – analysis output feeds visualization.
- **Management**: User roles restrict DB access; easy DB upload via UI.
- **Data**: User-uploaded SQLite files; results exported as PDFs.

**Simple Flow**: Query → Analyze → Visualize → Display

---

## Slide 3: Key Functions
**What Users Can Do**

- **Natural Language Queries**: "Show sales by country" – agents handle the rest.
- **Automated Analysis**: Extracts insights, tables, and viz recommendations.
- **Custom Visualizations**: Charts in company styles (e.g., professional, dark mode).
- **User Management**: Admins assign DB access; secure per-user restrictions.
- **Easy DB Integration**: Upload SQLite files, register instantly.
- **Export**: Download full PDF reports with summaries and charts.

**Example**: Upload Chinook DB, ask "Top-selling artists" → Get summary, table, bar chart.

---

## Slide 4: Design Decisions
**Why We Built It This Way**

- **Agent-Based**: Separated concerns (analysis vs. viz) for modularity and testing.
- **LangChain/LangGraph**: Handles LLM prompts and agent chaining reliably.
- **Streamlit for UI**: Quick to build, interactive – no complex web dev needed.
- **SQLite Focus**: Simple, file-based DBs for demos; scalable to other sources.
- **Guardrails**: Blocks unsafe code/SQL; retries LLM for clean output.
- **Testing**: Unit tests for agents, integration tests for workflow – ensures accuracy.

**Trade-Off**: Chose simplicity over advanced features (e.g., no real-time DBs) for quick wins.

---

## Slide 5: Future Improvements
**What's Next?**

- **Expand Data Sources**: Support CSV, APIs, or cloud DBs (e.g., PostgreSQL).
- **Advanced Viz**: Add interactive charts (Plotly) or AI-suggested custom styles.
- **Multi-Agent Scaling**: More agents (e.g., for data cleaning or ML predictions).
- **Performance**: Cache results, optimize LLM calls for faster responses.
- **Security**: Encrypt DBs, add audit logs for user actions.
- **UI Enhancements**: Mobile-friendly, CLI mode, or API for integrations.

**Vision**: Turn this into a full BI tool for non-technical users.

---

## Slide 6: Quality Assurance & Evaluation
**Ensuring Reliability and Safety**

- **Automated Testing**: 3+ unit tests per agent (e.g., accuracy checks on real data like Chinook DB); integration tests for full workflow.
- **Guardrails**: 
  - Analysis Agent: Blocks dangerous SQL keywords (e.g., 'DROP', 'DELETE'); validates query length.
  - Visualization Agent: Prevents unsafe code (e.g., 'os.system'); retries LLM for clean output; no 'with plt' context managers.
- **Evaluation Examples**: Tests verify correct summaries, tables, and charts; mock LLMs for consistent results.
- **Error Handling**: Fallbacks for failed viz (e.g., text-only insights); user-friendly error messages.

**Result**: High accuracy, secure execution – ready for production use.

---

## Slide 7: Demo Highlights & Q&A
**Live Demo Walkthrough**

- Upload a sample DB (e.g., Chinook music store).
- Run a query: "Total sales by country."
- See: Analysis summary, data table, generated bar chart.
- Export PDF report.
- Show user permissions and testing.

**Key Takeaways**: Agents automate complex tasks; easy to extend; ready for production.

Questions?
- `agents/visualization_agent.py`: Chart generation logic
- `agents/models.py`: Pydantic schemas for agent outputs
- `manager.py`: Database and user management functions

---

## Slide 7: User Experience
**How Users Interact**

1. **Login**: Select user role (admin, analyst, manager)
2. **Database Selection**: Choose from assigned databases
3. **Query Input**: Enter analysis request in natural language
4. **Theme Selection**: Pick visual style for reports
5. **Results View**: See summary, data table, and charts
6. **Export**: Download PDF report

---

## Slide 8: Security & Access Control
**Role-Based Permissions**

- **Admin**: Can upload databases and manage user permissions
- **Users**: Access only assigned databases
- **Database Registration**: Upload SQLite files through UI
- **Permission Management**: Admin panel for assigning access

---

## Slide 9: Demo Walkthrough
**Live Demonstration**

- Show the Streamlit interface
- Demonstrate database upload (admin)
- Run a sample analysis query
- View generated visualizations
- Export PDF report

---

## Slide 10: Benefits & Use Cases
**Why Use This Platform?**

- **Efficiency**: AI handles complex analysis automatically
- **Accessibility**: Natural language interface, no SQL required
- **Customization**: Multiple visual themes and export options
- **Scalability**: Modular agent design for adding new capabilities
- **Use Cases**: Business reporting, data exploration, quick insights

---

## Slide 11: Future Enhancements
**Potential Improvements**

- Support for additional database types (PostgreSQL, MySQL)
- More visualization types and interactive charts
- Advanced AI features (predictive analytics, anomaly detection)
- Multi-user collaboration features
- API endpoints for integration

---

## Slide 12: Q&A
**Questions?**

Thank you for your attention!

Contact: [Your Contact Information]