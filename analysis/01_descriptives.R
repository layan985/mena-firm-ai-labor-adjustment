suppressPackageStartupMessages({
  library(data.table)
  library(arrow)
  library(ggplot2)
})

path <- "data/processed/firm_year.parquet"
if (!file.exists(path)) stop("Missing data/processed/firm_year.parquet")
dt <- as.data.table(read_parquet(path))

print(dt[, .(
  firms = uniqueN(firm_id),
  observations = .N,
  adopters = uniqueN(firm_id[ai_score >= 2])
), by = .(country)])

p <- dt[, .(adoption_rate = mean(ai_score >= 2, na.rm = TRUE)), by = .(year)] |>
  ggplot(aes(year, adoption_rate)) +
  geom_line() + geom_point() +
  labs(x = NULL, y = "Share with substantive AI adoption")

dir.create("outputs/figures", recursive = TRUE, showWarnings = FALSE)
ggsave("outputs/figures/adoption_rate_by_year.pdf", p, width = 6.5, height = 4)
