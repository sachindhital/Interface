# 🏡 Property Insights Dashboard

A lightweight Flask + Chart.js dashboard that visualises real-time suburb-level property insights using the **Microburbs API Sandbox**.  
It transforms complex real estate, school, demographic, and development data into clear, interactive charts and tables — perfect for investors, analysts, and data enthusiasts.

---

## 🚀 Features

### 📊 1. Property Data
- Fetches “For Sale” listings for any Australian suburb  
- Displays:
  - Average property price
  - Median bedrooms
  - Most common property type  
- Includes a **bar chart** comparing average price by property type.

### 🎓 2. Schools
- Lists local schools with attendance rate, NAPLAN rank, and socioeconomic status  
- Includes a **performance chart** visualising NAPLAN scores per school.

### 👨‍👩‍👧‍👦 3. Demographics
- Visualises:
  - Population trend (line chart)
  - Age distribution (bar chart)
  - Income brackets (pie chart)

### 🏗️ 4. Developments
- Displays ongoing or recent building approvals (new dwellings, renovations, subdivisions)
- Sorted by date with description and category.

### 🌏 5. Ethnicity
- Aggregates suburb-level ethnic composition (e.g., Australians, Europeans, Asians)
- Shown as a **pie chart** with percentage breakdown.

### 💰 6. Pocket Prices
- Compares **median price and growth** across micro areas (SA1s) for houses and units  
- Includes dual-axis chart showing **average price ($)** and **average growth (%)**

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | Flask (Python) |
| Frontend | HTML + Jinja2 Templates |
| Charts | Chart.js |
| Data Handling | Pandas |
| API Source | [Microburbs API Sandbox](https://www.microburbs.com.au/report_generator/api/) |

---

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/property-insights-dashboard.git
cd property-insights-dashboard
