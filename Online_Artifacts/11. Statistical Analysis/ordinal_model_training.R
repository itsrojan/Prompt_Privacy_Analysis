library(brms)
library(readxl)
library(dplyr)
library(writexl)

INPUT_FILE <- "model_training_input.xlsx"

POSTERIOR_SUMMARY_EXCEL <- "brms_model_posterior_summary.xlsx"
MODEL_RDS <- "brms_ordinal_model.rds"

daf <- read_excel(INPUT_FILE)

cat("Raw shape:", nrow(daf), "rows x", ncol(daf), "cols\n")
cat("Columns:\n")
print(names(daf))

rename_map <- c(
  "_pid" = "_id",
  "rater_pid" = "rater_id"
)

for (old_name in names(rename_map)) {
  new_name <- rename_map[[old_name]]
  if (old_name %in% names(daf)) {
    names(daf)[names(daf) == old_name] <- new_name
  }
}

required_cols <- c(
  "prompt_id",
  "topic",
  "info_type",
  "party",
  "rater_id",
  "score",
  "rater_experience"
)

missing_required <- setdiff(required_cols, names(daf))
if (length(missing_required) > 0) {
  stop(paste("Missing required columns:", paste(missing_required, collapse = ", ")))
}

daf <- daf %>%
  mutate(score = suppressWarnings(as.numeric(score))) %>%
  filter(score %in% c(1, 2, 3, 4, 5)) %>%
  filter(
    !is.na(prompt_id),
    !is.na(topic),
    !is.na(info_type),
    !is.na(party),
    !is.na(rater_id),
    !is.na(score),
    !is.na(rater_experience)
  )

id_cols <- c(
  "prompt_id", "topic", "info_type",
  "party", "rater_id", "rater_experience"
)

for (col in id_cols) {
  daf[[col]] <- trimws(as.character(daf[[col]]))
}

co_cols <- grep("^co_", names(daf), value = TRUE)
cat("\nInitial number of co-occurrence columns:", length(co_cols), "\n")

for (col in co_cols) {
  daf[[col]] <- suppressWarnings(as.numeric(daf[[col]]))
  daf[[col]][is.na(daf[[col]])] <- 0
  daf[[col]] <- ifelse(daf[[col]] > 0, 1, 0)
}

# Force self co-occurrence to zero
for (i in seq_len(nrow(daf))) {
  target_col <- paste0("co_", daf$info_type[i])
  if (target_col %in% names(daf)) {
    daf[[target_col]][i] <- 0
  }
}

# Drop constant co_* columns
constant_co_cols <- co_cols[sapply(daf[co_cols], function(x) length(unique(x)) <= 1)]
if (length(constant_co_cols) > 0) {
  cat("\nDropping constant co-occurrence columns:\n")
  print(constant_co_cols)
  daf <- daf %>% select(-all_of(constant_co_cols))
}

co_cols <- grep("^co_", names(daf), value = TRUE)
cat("Remaining co-occurrence columns:", length(co_cols), "\n")
cat("Cleaned shape after constant column dropping:", nrow(daf), "rows x", ncol(daf), "cols\n")
print(names(daf))

# Ordered outcome for ordinal regression
daf$score <- ordered(daf$score, levels = c(1, 2, 3, 4, 5))

# Grouping variables as factors
factor_cols <- c("prompt_id", "topic", "info_type", "party", "rater_id", "rater_experience")
for (col in factor_cols) {
  daf[[col]] <- as.factor(daf[[col]])
}

# Prompt-rater interaction grouping factor
daf$prompt_rater <- interaction(daf$prompt_id, daf$rater_id, drop = TRUE)

cat("\nData ready for modeling.\n")
cat("Rows:", nrow(daf), "\n")
cat("Unique prompts:", nlevels(daf$prompt_id), "\n")
cat("Unique raters:", nlevels(daf$rater_id), "\n")
cat("Unique info types:", nlevels(daf$info_type), "\n")
cat("Unique prompt-rater pairs:", nlevels(daf$prompt_rater), "\n")

fixed_terms <- c("party", "topic", "rater_experience", co_cols)
fixed_part <- paste(fixed_terms, collapse = " + ")

formula_string <- paste0(
  "score ~ ",
  fixed_part,
  " + (1 | info_type)",
  " + (1 | prompt_id)",
  " + (1 | rater_id)",
  " + (1 | prompt_rater)"
)

cat("\nModel formula:\n")
cat(formula_string, "\n")

model_formula <- bf(as.formula(formula_string))

priors <- c(
  prior(normal(0, 1), class = "b"),
  prior(normal(0, 1), class = "Intercept"),
  prior(exponential(10), class = "sd")
)

fit <- brm(
  formula = model_formula,
  data = daf,
  family = cumulative(link = "logit"),
  prior = priors,
  chains = 4,
  cores = 4,
  iter = 4000,
  warmup = 2000,
  seed = 42,
  control = list(adapt_delta = 0.95)
)

saveRDS(fit, MODEL_RDS)

summary_obj <- summary(fit)
print(summary_obj)

# Fixed effects
fixed_df <- as.data.frame(fixef(fit))
fixed_df$term <- rownames(fixed_df)

# Random effects: info_type
ranef_info_type <- as.data.frame(ranef(fit)$info_type[, , "Intercept"])
ranef_info_type$info_type <- rownames(ranef(fit)$info_type[, , "Intercept"])

# Random effects: prompt_id
ranef_prompt <- as.data.frame(ranef(fit)$prompt_id[, , "Intercept"])
ranef_prompt$prompt_id <- rownames(ranef(fit)$prompt_id[, , "Intercept"])

# Random effects: rater_id
ranef_rater <- as.data.frame(ranef(fit)$rater_id[, , "Intercept"])
ranef_rater$rater_id <- rownames(ranef(fit)$rater_id[, , "Intercept"])

# Random effects: prompt_rater
ranef_prompt_rater <- as.data.frame(ranef(fit)$prompt_rater[, , "Intercept"])
ranef_prompt_rater$prompt_rater <- rownames(ranef(fit)$prompt_rater[, , "Intercept"])

write_xlsx(
  list(
    fixed_effects = fixed_df,
    info_type_effects = ranef_info_type,
    prompt_effects = ranef_prompt,
    rater_effects = ranef_rater,
    prompt_rater_effects = ranef_prompt_rater
  ),
  POSTERIOR_SUMMARY_EXCEL
)

cat("\nModel fit completed.\n")
cat("Model saved to:", MODEL_RDS, "\n")
cat("Posterior summary saved to:", POSTERIOR_SUMMARY_EXCEL, "\n")