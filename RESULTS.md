# Results

The Medical Report Tracker successfully demonstrates the practical application of RAG technology in healthcare data management. The system effectively processes multiple lab reports, extracts patient information and test results, and provides accurate, context-aware responses to natural language queries about patient health metrics.

## Query Examples and Responses

The system successfully answers various types of questions with detailed, data-driven responses. Below are examples demonstrating the system's capabilities:

### Example 1: Specific Metric Inquiry

**Question:** "What is the patient's current hemoglobin level?"

**Response:**
> The patient's current hemoglobin level is 16.73 g/dL, as reported in KRAUSE's lab report #4

### Example 2: Trend Analysis

**Question:** "Show me the trend in triglyceride levels"

**Response:**
> The triglyceride levels for KRAUSE, LAUREN over the reported periods are as follows:
> 
> - Report #1 (12/08/2025): 88.11 mg/dL (within the reference range of 50-150 mg/dL)
> - Report #2 (01/08/2026): 134.77 mg/dL (within the reference range of 50-150 mg/dL)
> - Report #3 (02/08/2026): 61.98 mg/dL (within the reference range of 50-150 mg/dL)
> - Report #4 (03/08/2026): 79.05 mg/dL (within the reference range of 50-150 mg/dL)
> 
> **Trend Analysis:**
> - The triglyceride levels started at 88.11 mg/dL, increased to 134.77 mg/dL, then decreased to 61.98 mg/dL, and finally rose again to 79.05 mg/dL.
> - Overall, there is a fluctuation in the triglyceride levels, with a peak in January 2026, followed by a decrease in February and a slight increase in March.

### Example 3: Comprehensive Test Results

**Question:** "What are the patient's liver function test results?"

**Response:**
> The liver function test results for the patient KRAUSE are as follows:
> 
> **Report #1:**
> - Protein, Total: 7.1 g/dL (Reference range: 6.1-8.1 g/dL)
> - AST: 30 U/L (Reference range: 10-40 U/L)
> - ALT: 7 U/L (Reference range: 9-46 U/L, noted as low)
> 
> **Report #2:**
> - Protein, Total: 6.54 g/dL (Reference range: 6.1-8.1 g/dL)
> - AST: 23 U/L (Reference range: 10-40 U/L)
> - ALT: 18 U/L (Reference range: 9-46 U/L)
> 
> **Report #3:**
> - Protein, Total: 7.11 g/dL (Reference range: 6.1-8.1 g/dL)
> - AST: 47 U/L (Reference range: 10-40 U/L, noted as high)
> - ALT: 58 U/L (Reference range: 9-46 U/L, noted as high)
> 
> **Report #4:**
> - Protein, Total: 6.88 g/dL (Reference range: 6.1-8.1 g/dL)
> - AST: 12 U/L (Reference range: 10-40 U/L)
> - ALT: 43 U/L (Reference range: 9-46 U/L)
> 
> In summary, the AST and ALT levels vary across the reports, with some values being high or low compared to the reference ranges.

## Key Achievements

The system successfully demonstrates accurate retrieval of specific values, trend analysis across multiple time periods, and comprehensive reporting of test results with reference ranges. Patient-specific filtering ensures responses are scoped to the selected patient's data, and the natural language interface eliminates the need for complex database queries. The RAG pipeline effectively processes unstructured PDF documents and enables intuitive querying of longitudinal patient data.
