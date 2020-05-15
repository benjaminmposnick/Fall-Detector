library(ggplot2)

# Read in data
type <- time_v_size$V1
batch_size <- time_v_size$V2[time_v_size$V1=="point"]
resp_time <- time_v_size$V3[time_v_size$V1=="point"]

# Violin plots of response time vs. batch size
df1 <- data.frame("Batch Size" = batch_size, "Response Time (s)" = resp_time)
ggplot(df1, aes(x=factor(batch_size), y=resp_time)) +
  geom_violin(aes(fill = factor(batch_size))) +
  geom_boxplot(width=0.2, outlier.shape = NA) +
  labs(title="Response time vs. batch size when\nconducting inference at ACI endpoint", 
       x="Batch size",
       y = "Response time (s)",
       fill = "Batch size")

# Scatter plot of response time per example in batch vs. batch size
mean_bs <- time_v_size$V2[time_v_size$V1=="mean"]
mean_rt <- time_v_size$V3[time_v_size$V1=="mean"]
df2 <- data.frame("Batch Size" = batch_size, "Response time per example" = resp_time/batch_size)
ggplot(df2, aes(x=factor(batch_size), y=resp_time/batch_size, color=resp_time/batch_size)) +
  geom_point() +
  theme_minimal() +
  scale_color_gradient(low = "#0091ff", high = "#f0650e") +
  labs(title="Response time per example in batch vs. batch\nsize when conducting inference at ACI endpoint", 
      x="Batch size",
      y = "Response time per example in batch (s)",
      fill = "Ratio") +
  scale_y_continuous(trans='log10')

# Variance in response time per example in batch
N <- length(mean_bs)
vars <- rep(0, N)
sizes <- rep(0, N)
for (i in 1:N-1) {
  bs <- 2^i
  sizes[i] <- bs
  vars[i] = var(resp_time[batch_size==bs]/bs)
}
#plot(sizes, vars, log="xy")
         