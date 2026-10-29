# Product Requirements Document (PRD)
## Multi-Agent AI Demonstration: Game Theory Suite

### 1. Project Overview & Vision
This project demonstrates the end-to-end orchestration of modern Generative AI tools to teach, visualize, and interact with foundational Game Theory concepts. The project encompasses theoretical presentations, generative AI video simulations, and an interactive cloud-deployed game solver.

---

### 2. Core Pillars & Deliverables
1. **Interactive Academic Presentation:** Comprehensive theoretical review of Game Theory, dominant strategies, Nash Equilibrium, and sequential zero-sum games with imperfect information.
2. **Generative AI Video Simulation (Prisoner's Dilemma):** A cinematic AI-generated conceptual video visualizing strategic defection vs. cooperation.
3. **Interactive Kuhn Poker GTO Engine (Python / Streamlit):** An interactive web application allowing users to play against a Nash Equilibrium (Game Theory Optimal) agent in real-time, deployable via mobile QR scanning.
4. **Engineering Traceability:** Comprehensive documentation of prompt engineering pipelines, version-controlled iterations, and collaborative workflow.

---

### 3. Functional Requirements (Kuhn Poker Interactive App)
* **Game Rules Engine:** Strict Kuhn Poker mechanics (3-card deck: J, Q, K; 1-chip ante; 1-chip bet).
* **Strategic Solver:** GTO computation matching Nash equilibrium frequencies (optimal bluffing $\alpha = 1/3$ for Player 1 with Jack, calling frequencies for Player 2).
* **State Management:** Session-persistent chips tracking, active game history log, and responsive dynamic action triggers.
* **Dual Roles:** Dynamic toggle between playing as Player 1 (out of position) and Player 2 (in position).
* **Interactive UI:** Casino-themed poker table with visual indicators for pot size, hole cards, actions, and real-time GTO feedback.

---

### 4. Non-Functional Requirements
* **Cloud Accessibility:** Deployed publicly on Streamlit Community Cloud with high availability.
* **Zero-Install Client:** Fully accessible from mobile devices via dynamic QR code embedded in lecture slides.
* **Codebase Maintainability:** Clean separation of game logic (`Poker.py`) and presentation layer (`app.py`).

---

### 5. AI Tooling Stack
* **Language & Architecture Models:** Claude, Gemini (Game Engine Logic, Mathematical Solvers, PRD/README synthesis).
* **Code Frameworks:** Python 3.12, Streamlit, Git.
* **Generative Video & Media:** AI Video Generator (Prisoner's Dilemma visualization).
