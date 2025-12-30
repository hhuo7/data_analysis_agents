# Demo Slides: AI Agents for Data Analysis Platform

## Slide 1: Title Slide
**AI Agents for Data Analysis and Visualization**

- A Streamlit-based Business Intelligence platform
- Powered by AI agents for automated data analysis
- Presented by: [Your Name]
- Date: December 29, 2025

---

## Slide 2: Overview
**What is this platform?**

- **Purpose**: Automate data analysis and visualization using AI
- **Key Features**:
  - Natural language queries for data analysis
  - AI-generated visualizations and reports
  - Role-based access control for databases
  - PDF export of complete reports
- **Technology Stack**: Python, Streamlit, LangChain, OpenAI GPT, SQLite

---

## Slide 3: System Architecture
**High-Level Structure**

- **Frontend**: Streamlit web app (app.py)
- **Backend Agents**:
  - Analysis Agent: Processes queries, generates summaries
  - Visualization Agent: Creates plotting code
  - Workflow Orchestrator: LangGraph for agent coordination
- **Management Layer**: User and database permissions (manager.py)
- **Data Layer**: SQLite databases stored in /data folder

---

## Slide 4: Workflow Diagram
**How It Works**

1. User selects database and enters natural language query
2. Analysis Agent queries database and generates structured report
3. Visualization Agent creates Python plotting code
4. Streamlit displays results and allows PDF export

**Agent State Flow**:
User Query → Analysis Report → Visualization Code → Final Output

---

## Slide 5: Design Decisions
**Why These Choices?**

- **AI Agents**: Automates complex analysis tasks, reduces manual coding
- **LangGraph**: Provides structured workflow management for multi-agent systems
- **Pydantic Models**: Ensures type safety and structured outputs from agents
- **Streamlit**: Rapid web app development, perfect for data apps
- **SQLite for Management**: Lightweight, file-based database for user permissions
- **Style Configurations**: Allows customizable visual themes for reports

---

## Slide 6: Key Components
**Core Files and Modules**

- `app.py`: Main UI with tabs for analysis and admin
- `agents/workflow.py`: LangGraph workflow definition
- `agents/analysis_agent.py`: Data querying and summarization
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