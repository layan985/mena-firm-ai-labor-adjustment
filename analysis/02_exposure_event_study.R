suppressPackageStartupMessages({
  library(data.table)
  library(arrow)
  library(fixest)
})

path <- "data/processed/firm_year.parquet"
if (!file.exists(path)) stop("Missing processed firm-year panel")
dt <- as.data.table(read_parquet(path))

required <- c("firm_id","country","sector","year","log_employment","pre_ai_exposure")
stopifnot(all(required %in% names(dt)))

dt[, event_year := year - 2022L]

# Continuous-treatment event study. Reference year = 2021 (event_year = -1).
# Country-by-year FE absorb country-specific annual shocks.
# Sector-specific linear trends absorb differential secular trajectories.
m <- feols(
  log_employment ~ i(event_year, pre_ai_exposure, ref = -1) | firm_id + country^year + sector[year],
  cluster = ~sector,
  data = dt
)

print(summary(m))
dir.create("outputs/models", recursive = TRUE, showWarnings = FALSE)
saveRDS(m, "outputs/models/exposure_event_study.rds")
