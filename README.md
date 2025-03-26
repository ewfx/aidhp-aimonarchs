# 🚀 FinPersona : A Gen-AI Based Hyper-Personalized Banking Recommendation System

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
Our solution - FinPersona is an advanced, real-time AI-driven banking recommendation platform that delivers hyper-personalize product/service recommendations and financial insights. The system analyzes customer data across multiple dimensions based on thier transactions, financial goals, and, feedback to provide tailored financial guidance, helping users make better financial decisions while enabling our bank to offer more relevant products and services.

## 🎥 Demo
📹 Video demo -  
🖼️ Screenshots -

![Screenshot 1](link-to-image)

## 💡 Inspiration
The inspiration behind our solution came from observing the disconnect between modern banking products and individual customer needs. Traditional banking recommendations are often generic and fail to consider the nuanced financial situations of users. We saw an opportunity to transform the banking experience by creating a system that truly understands each customer's financial profile, behavior patterns, and goals, then delivers tailored guidance that feels like having a personal financial advisor available 24/7.

## ⚙️ What It Does
FinPersona project offers a comprehensive suite of personalized financial tools:

1.	*Intelligent Dashboard -* Provides a real-time financial health overview with AI-generated insights about spending patterns, interactive expense breakdowns, 6-month trend analysis, and spotlight recommendations.
2.	*Hyper-Personalized Recommendations -* Delivers financial product suggestions with percentage match scores, contextual reasoning for each recommendation, highlighting of most relevant features, and interactive feedback capabilities.
3.	*Transaction Intelligence -* Analyzes financial behavior through sentiment analysis, detects spending anomalies, displays categorized transaction timelines, provides predictive insights on upcoming expenses, and identifies optimization opportunities.
4.	*AI Financial Assistant -* Features a natural language interface that understands financial questions, maintains contextual awareness across conversations, offers personalized advice, and provides goal-oriented guidance through multi-turn reasoning.
5.	*Data Integration & Security -* Ensures secure management of financial data with robust MongoDB schema design, automatic transaction categorization, comprehensive user profiling, and privacy-preserving analysis.

## 🛠️ How We Built It
We have used a modern technology stack designed for scalability, security, and high performance to develop our solution:

- For the frontend, we implemented a responsive interface using React.js with Material UI components that provide a professional financial design aesthetic. Data visualizations were created using Recharts for clear representation of financial metrics and trends. Axios handles API communication with our backend services.
- The backend infrastructure is built on FastAPI, a high-performance Python framework ideal for financial data processing. We chose MongoDB as our database solution for its flexible document structure, which accommodates complex financial data relationships. Custom Python analytics power our financial analysis algorithms.
- The AI/ML components include specialized models for sentiment analysis of financial behavior, a hybrid recommendation engine combining collaborative and content-based filtering, natural language processing for our conversational assistant, and statistical methods for anomaly detection in financial activities.

## 🚧 Challenges We Faced
Understanding the essence of the problem statemnt and developing a solution keeping the requirements was definitely quite challenging for us. While developing our soltion we did face the following significant challenges:

1.	*Recommendation Relevance -* Creating an algorithm that delivers truly personalized recommendations rather than generic suggestions demanded extensive refinement of our matching algorithms.
2.	*Financial Sentiment Analysis -* Developing models to accurately interpret financial behaviors as positive or negative required domain-specific training data and expert validation.
3.	*Contextual Understanding -* Enabling the AI assistant to maintain meaningful financial conversations across multiple messages required advanced NLP techniques and memory management.
4.	*Integration Complexity -* Connecting various data sources while maintaining data integrity and performance presented significant architectural challenges.
5.	*Data Privacy and Security -* Balancing the need for comprehensive financial analysis while protecting sensitive user information required sophisticated anonymization and security protocols.

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/https://github.com/ewfx/aidhp-aimonarchs.git
   ```
   
2. Install dependencies
   
   For frontend dependencies: 
   ```sh
   npm install
   ```
   
   For backend packages:
   ```sh
   pip install -r requirements.txt
   ```
   
4. Run the project
   
   To run frontend: 
   ```sh
   npm start
   ```
   
   To run backend:
   ```sh
   uvicorn app.main:app --reload
   ```
   
## 🏗️ Tech Stack
- 🔹 Frontend: React.js, Material UI, Recharts
- 🔹 Backend: FastAPI, Python
- 🔹 Database: MongoDB
- 🔹 AI/ML: BERT, Custom sentiment analysis, hybrid recommendation engine, Google NLP models

## 👥 Team
- **Bhavini Singh** - https://github.com/Bhavini20/ | https://www.linkedin.com/in/bhavinisingh18/
- **Samriddhi Agarwal** - https://github.com/samriddhiag19 | https://www.linkedin.com/in/samriddhi-agarwal-1903y2001/
- **Vanshita Singh** - https://github.com/Vanshitasingh | https://www.linkedin.com/in/vanshita-singh-277aa21b2/
- **Viswonathan Manoranjan** - https://github.com/Viswonathan06 | https://www.linkedin.com/in/viswonathan-manoranjan/
- **Teammate 2** - [GitHub](#) | [LinkedIn](#)
