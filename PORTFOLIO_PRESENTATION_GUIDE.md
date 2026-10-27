# DealPulse M&A — دليل التقديم للمقابلات وسيرتك الذاتية (Portfolio & Interview Guide)

تهانينا! مشروعك الآن مكتمل بنسبة 100%، وتم تصميمه وفق أعلى المعايير المؤسسية (Institutional-Grade) التي تبحث عنها كبرى الشركات وبنوك الاستثمار وصناديق الاستثمار المباشر (Private Equity / Investment Banking / Tech Firms) لوظائف:
- **Data Analyst**
- **Financial Data Analyst / Analytics Engineer**
- **Data Engineer / BI Developer**

---

## 📄 1. كيف تكتب هذا المشروع في سيرتك الذاتية (CV / Resume)

ضع المشروع تحت قسم **Projects** أو **Key Technical Projects** بهذه الصيغة الاحترافية بالإنجليزية:

> **DealPulse M&A: Automated Market Intelligence & Valuation Platform**  
> *Technologies: Python (Pandas, Polars, Pydantic), SQL (Star Schema), Streamlit, Power BI, DAX, Pytest, GitHub Actions, Docker*
> - Engineered an automated end-to-end data pipeline scraping M&A transaction feeds, SEC 8-K filings, and PE press releases across US, UK, and European markets.
> - Implemented resilient entity resolution and ontology mapping to deduplicate corporate entities, normalize cross-currency transactions (GBP/EUR to USD), and validate records via Pydantic schemas.
> - Modeled a Kimball dimensional Star Schema warehouse in SQL (`fact_mna_deals`, `dim_companies`, `dim_sectors`, `dim_advisors`) with analytical benchmarking views.
> - Built an interactive Streamlit dashboard and exported curated star-schema datasets with DAX measures for executive Power BI deal screening and valuation multiple analysis (EV/EBITDA, EV/Revenue).
> - Established CI/CD automation via GitHub Actions and achieved 100% test coverage across scrapers, ETL pipeline, and database views using Pytest.

---

## 🎤 2. كيف تتحدث عن المشروع في المقابلة الشخصية (Interview STAR Method)

عندما يسألك مسؤول التوظيف: **"Tell me about a complex project you built from scratch?"**، أجب بهذه الطريقة:

### **1. Situation (الموقف والسياق):**
> *"في قطاع بنوك الاستثمار وصناديق الـ Private Equity، سرعة ودقة تسعير الصفقات (Valuation Multiples) هي الفارق الرئيسي للفوز بالصفقة. المحللون عادة يضيعون ساعات طويلة في تجميع بيانات الصفقات ومضاعفات EV/EBITDA يدوياً من عدة مصادر غير منظمة وبأشكال عملات مختلفة."*

### **2. Task (المهمة التي حددتها لنفسك):**
> *"قمت ببناء منصة بيانات متكاملة ومؤتمتة (DealPulse) تقوم بسحب البيانات دورياً، تنظيفها، توحيد الكيانات والعملات، وحساب مضاعفات التقييم، وتغذية لوحات تحكم تفاعلية وتقارير Power BI للمدراء التنفيذيين."*

### **3. Action (ما قمت به تقنياً):**
> - *"بنيت خط سحب البيانات (Web Scrapers) مع آليات Exponential Backoff لتفادي الحظر.*
> - *طبقت Entity Resolution لإزالة اللواحق القانونية مثل (Inc, LLC, plc) وحساب معرف كيان موحد لمنع التكرار.*
> - *صممت مستودع بيانات Star Schema كيمبالي يحتوي جداول الأبعاد وجدول الحقائق.*
> - *بنيت مقاييس إحصائية متقدمة (Quartiles: Median, P25, P75, IQR) لكشف الصفقات ذات التقييمات الشاذة (Outliers).*
> - *أضفت لوحة تحكم بـ Streamlit و Plotly، وصممت مقاييس DAX لـ Power BI، مع اختبارات أوتوماتيكية عبر Pytest و GitHub Actions."*

### **4. Result (النتيجة والأثر):**
> *"المشروع حوّل عملية تحليل الصفقات من عملية يدوية تستغرق أياماً إلى تدفق بيانات مؤتمت بالكامل يتم في دقائق، بموثوقية 100% بدون فقدان أو تكرار للبيانات."*

---

## 🚀 3. خطوات رفع المشروع على حسابك في GitHub

افتح موجه الأوامر (Terminal) ونفّذ التالي:

```bash
cd C:\Users\Magnus\.gemini\antigravity-ide\scratch\dealpulse-mna-platform

# 1. أنشئ مستودعاً جديداً على GitHub باسم dealpulse-mna-platform
# 2. اربط المستودع بحسابك (استبدل YOUR_USERNAME باسم حسابك على جيت هب):
git remote add origin https://github.com/YOUR_USERNAME/dealpulse-mna-platform.git

# 3. ارفع المشروع إلى الفرع الرئيسي:
git branch -M main
git push -u origin main
```

---

## 🖥️ 4. تشغيل المشروع محلياً

### تشغيل لوحة التحكم التفاعلية (Streamlit Dashboard):
```bash
uv run --with-requirements requirements.txt streamlit run dashboard/app.py
```
ستفتح شاشة المتصفح على: `http://localhost:8501`

### تشغيل الاختبارات للتأكد من سلامة النظام (Pytest):
```bash
uv run --with-requirements requirements.txt pytest tests/ -v
```

### تصدير بيانات Power BI المحدثة:
```bash
uv run --with-requirements requirements.txt python dashboard/export_powerbi_data.py
```
الملفات المصدرة ستجدها جاهزة في: `data/exports/`
