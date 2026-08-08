suppressPackageStartupMessages({
  library(data.table)
  library(arrow)
  library(fixest)
})

path <- "data/processed/wbes_mena.parquet"
if (!file.exists(path)) stop("Missing WBES processed data")
dt <- as.data.table(read_parquet(path))

# Supportive association/change model. Do not call this causal merely because it is a change outcome.
m <- feols(
  employment_log_change_3y ~ I(ai_score >= 2) + log1p(l2) + firm_size_pre + exporter + foreign_owned | country + sector,
  vcov = ~country,
  weights = ~survey_weight,
  data = dt
)
print(summary(m))
