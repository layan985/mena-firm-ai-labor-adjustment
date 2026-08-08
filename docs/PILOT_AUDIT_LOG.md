# Pilot audit log: first real corporate disclosures

This log records the first public-source rows used to stress-test the repository against real annual-report messiness. It is deliberately separate from the synthetic CI fixture and from any future inferential dataset.

## 1. Saudi Aramco — clean comparable workforce series, left-censored AI adoption

The 2025 Annual Report sustainability section reports company employees for 2021–2025 as 68,493; 70,496; 73,311; 75,118; and 76,664, respectively, with female employee shares of 5.6%, 6.4%, 7.2%, 7.9%, and 8.2%. The reporting scope is explicitly the Saudi Arabian Oil Company.

AI evidence is already substantive in the 2020 report, which says Aramco is bringing digitization, automation, and AI to its core business. Therefore, the first-adoption year cannot responsibly be coded as 2020: adoption is left-censored and earlier reports must be reviewed. By 2024, the report describes an industrial LLM used to provide workforce knowledge/advice and power real-time advisory systems. The 2025 report documents further scaling of AI compute capacity.

**Decision:** Aramco can enter the exposure design and descriptive technology-intensity analysis. It must not enter a staggered-adoption cohort with an invented 2020 treatment date.

## 2. stc — large headcount movement that must not be naively interpreted

The 2023 business-model disclosure reports 22,751 group employees. The 2024 business-model disclosure reports 19,863. The 2023 report also says a three-year workforce right-sizing strategic plan was developed to commence in 2024.

A naive year-on-year regression would treat the roughly 13% fall as a labor-market outcome. That is unacceptable without auditing the group perimeter, TAWAL/other transactions, discontinued operations, and reporting definitions.

**Decision:** the pipeline now automatically flags absolute annual headcount changes of at least 10% for structural-break review. A flag is not an exclusion; it forces documentation before estimation.

## 3. Almarai — reporting-scope discipline and a clean treatment-timing lesson

Almarai's 2025 financial-statement disclosure reports 46,997 GCC employees in 2025 and 43,918 in 2024 within employee-benefit demographic assumptions. Elsewhere, the business-model page says the workforce is 50,000+ employees. These are not interchangeable measures.

The 2024 technology discussion explicitly describes generative AI and decision intelligence as technologies to be deployed over the next few years, so that language is coded as planning/rhetoric rather than treatment. The 2025 digital-transformation disclosure says Almarai expanded AI productivity tools and established an AI Centre of Excellence. This is provisionally coded score 2, subject to tool-level manual validation.

**Decision:** provisional adoption year = 2025 for the public seed. The 2024 row is a pre-treatment planning signal, not a treated observation.

## What this pilot changes in the full study

1. Treatment dates may be left-censored; those firms need a separate status rather than a guessed first year.
2. Workforce measures require an explicit reporting-scope identifier.
3. Large headcount changes trigger a corporate-action/restructuring audit.
4. Forward-looking AI language is not adoption.
5. The 50-firm pilot must be a schema and extraction stress test, not an inferential convenience sample.
