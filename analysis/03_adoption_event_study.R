suppressPackageStartupMessages({
  library(data.table)
  library(arrow)
  library(fixest)
  library(did)
})

path <- "data/processed/firm_year.parquet"
if (!file.exists(path)) stop("Missing processed firm-year panel")
dt <- as.data.table(read_parquet(path))

dt[, first_ai_year_cs := fifelse(is.na(first_ai_year), 0L, as.integer(first_ai_year))]

# Sun-Abraham dynamic specification. Adoption is endogenous; treat as event-time evidence
# unless a stronger identification argument survives diagnostics.
sa <- feols(
  log_employment ~ sunab(first_ai_year, year, ref.p = -1) | firm_id + country^year,
  cluster = ~firm_id,
  data = dt
)
print(summary(sa))

# Callaway-Sant'Anna group-time ATT.
cs <- att_gt(
  yname = "log_employment",
  tname = "year",
  idname = "firm_id",
  gname = "first_ai_year_cs",
  data = as.data.frame(dt),
  panel = TRUE,
  control_group = "notyettreated",
  clustervars = "firm_id"
)
print(summary(aggte(cs, type = "dynamic")))

dir.create("outputs/models", recursive = TRUE, showWarnings = FALSE)
saveRDS(sa, "outputs/models/adoption_sunab.rds")
saveRDS(cs, "outputs/models/adoption_cs.rds")
