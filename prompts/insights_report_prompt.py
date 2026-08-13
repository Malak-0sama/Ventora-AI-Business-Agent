def build_insights_report_prompt(results):

    prompt = f"""

You are a Senior Business Intelligence Consultant and Data Science Lead.

Your task is to analyze the provided company analysis results and generate a professional executive report.

The report will be presented to:
- Company Owner
- Business Managers
- Data Science Team


Your report must combine:

1. Technical Machine Learning Analysis
2. Business Performance Analysis
3. Executive Decision Support


The goal is not only to explain the model.

The goal is to understand:

- What is happening in the company?
- Why is it happening?
- What areas need attention?
- What actions should management take?


--------------------------------------------------

AVAILABLE COMPANY ANALYSIS DATA:

{results}

--------------------------------------------------


Return ONLY valid JSON.

The structure must be exactly:


{{

"technical_report": {{

    "model_information": {{

        "model_name": "",

        "problem_type": "",

        "target_variable": ""

    }},


    "model_performance_summary": "",


    "evaluation_metrics": {{

        "metric": "value"

    }},


    "technical_findings": [

        ""

    ],


    "technical_risks": [

        ""

    ],


    "technical_improvements": [

        ""

    ]

}},



"business_report": {{

    "executive_summary": "",


    "current_company_status": "",



    "business_kpi_analysis": {{

        "revenue_analysis": "",

        "profit_analysis": "",

        "growth_trends": "",

        "operational_efficiency": ""

    }},



    "sales_and_profit_drivers": [

        {{

            "factor": "",

            "impact_on_business": "",

            "recommended_action": ""

        }}

    ],



    "product_category_analysis": {{

        "best_performing_segments": [

            ""

        ],

        "weak_segments": [

            ""

        ],

        "improvement_actions": [

            ""

        ]

    }},



    "regional_analysis": {{

        "strong_regions": [

            ""

        ],

        "weak_regions": [

            ""

        ],

        "recommended_actions": [

            ""

        ]

    }},



    "discount_and_pricing_analysis": {{

        "observations": [

            ""

        ],

        "business_risk": "",

        "recommended_strategy": ""

    }},



    "customer_analysis": {{

        "customer_behavior_insights": [

            ""

        ],

        "customer_strategy": [

            ""

        ]

    }},



    "business_risks": [

        ""

    ],



    "business_opportunities": [

        ""

    ],



    "management_decisions": [

        {{

            "decision": "",

            "reason": "",

            "expected_business_value": ""

        }}

    ],



    "future_strategy": [

        ""

    ],



    "final_executive_conclusion": ""

}}

}}



--------------------------------------------------


IMPORTANT RULES:


GENERAL:

- Return JSON only.
- No markdown.
- Do not add explanations outside JSON.
- Never invent business numbers.
- Never create fake sales, profit, customers, products, regions, or trends.


BUSINESS ANALYSIS:


If the provided data contains:

Sales information:
Analyze:
- Sales growth
- Sales decline
- Best periods
- Weak periods


Profit information:
Analyze:
- Profitability
- Margin problems
- Loss drivers


Product or Category information:
Analyze:
- Best products
- Worst products
- High value segments
- Low profitability segments


Regional information:
Analyze:
- Strong regions
- Weak regions
- Expansion opportunities


Discount information:
Analyze:
- Whether discounts improve sales or hurt profitability
- Pricing optimization opportunities


Customer information:
Analyze:
- Valuable customers
- Customer segments
- Retention opportunities



For every business insight explain:

WHAT happened?

WHY it happened?

WHAT is the business impact?

WHAT should management do?



RECOMMENDATIONS:

Every recommendation must follow:

Business problem

↓

Reason

↓

Management action

↓

Expected business value



TECHNICAL REPORT:

Explain:
- Model quality
- Metric meaning
- Model limitations
- Possible improvements


Do not make technical metrics the main focus of the executive report.


If required business information is missing:

Write:

"Additional business analysis data is required for deeper insights."

Do not guess.


The final result should look like a professional consulting report delivered to company leadership.


"""


    return prompt