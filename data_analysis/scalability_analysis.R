# library(ggplot2)

# Read data
oneServer <- read.csv(file="scalability_test.csv",sep=",",head=TRUE)
twoServer <- read.csv('scalability_test_2.csv', sep = ",",head=TRUE)
threeServer <- read.csv('scalability_test_3.csv', sep = ",",head=TRUE)
fourServer <- read.csv('scalability_test_4.csv', sep = ",",head=TRUE)

# Calculate quantiles and averages
one95 <- quantile(oneServer$resp_time, .95)
two95 <- quantile(twoServer$resp_time, .95)
three95 <- quantile(threeServer$resp_time, .95)
four95 <- quantile(fourServer$resp_time, .95)
Percentiles_95th <- c(one95, two95, three95, four95)

oneMean <- oneServer$resp_time[oneServer$point=="mean"]
twoMean <- twoServer$resp_time[twoServer$point=="mean"]
threeMean <- threeServer$resp_time[threeServer$point=="mean"]
fourMean <- fourServer$resp_time[fourServer$point=="mean"]
Mean_times <- c(oneMean, twoMean, threeMean, fourMean)

oneMin <- min(oneServer$resp_time)
twoMin <- min(twoServer$resp_time)
threeMin <- min(threeServer$resp_time)
fourMin <- min(fourServer$resp_time)
minTimes <- c(oneMin, twoMin, threeMin, fourMin)

oneMax <- max(oneServer$resp_time)
twoMax <- max(twoServer$resp_time)
threeMax <- max(threeServer$resp_time)
fourMax <- max(fourServer$resp_time)
maxTimes <- c(oneMax, twoMax, threeMax, fourMax)

Number_homes <- c(1,2,3,4)

png(file="scalability.png")

plot(Number_homes, Percentiles_95th,
main="Scalability Analysis: # Homes vs Response Time Metrics",
ylab="Response Times (s)",
xlab="Number of Homes",
xlim=c(1,4),
ylim=c(0.043,0.09),
# ylim=c(0.058,0.065),
xaxt = "n",
type="l",
col="blue")
axis(1, at = 1:4)
lines(Number_homes, Mean_times, col="red")
lines(Number_homes, minTimes, col="green")
lines(Number_homes, maxTimes, col="orange")
legend("topleft",
c("95th Percentile", "Mean", "Min", "Max"),
fill=c("blue","red", "green", "orange"))


