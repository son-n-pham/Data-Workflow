## Challenges when looking for MSE min:

### The main challenge is from several factors:

- The nature of data, which we are drilling very low ROP (1-2m/h) and resolution is 0.25m (relatively not enough resolution to capture the drilling performance)
- WOB value is tricky and sometimes incorrect (negative or very low numbers). Alternative option such as hook load might need to be considered to reduce the risk of WOB error.
- The nature of the optimization algorithm: Initial parameters are generated randomly, then the Monte Carlo simulation is using the optimization algorithm to minimize MSE as much as it can. Due to the 2 points above, the algorithm sometimes gets stuck in the extreme values, usually very low (near 0 or equal to 0) or very high. Constraint of WOB, TORQUE, Mu is put into the optimization functions to minimize the impact, which improve the quality but still does not good enough to prevent some extreme cases.

### Solution:

- Several trial-and-error, and careful inspection on the result and compare to reality have been done. We also try other solutions of different ways to generate random numbers.
- The final result from careful tweaking the constraints on drilling parameters has given the most reasonable results.
- Another improvement is to print out the result of median and IQR instead of min and max values of the parameters and predicted result as the min and max values are just causing unnecessary confusion. Experiment that mean and standard deviation can also be heavily impact by outliers and showed misleading info/result.
  - One middle measurement that is not significantly impacted by outliers is the median. The median is the middle value of a dataset when it is sorted in ascending or descending order. It divides the dataset into two equal halves. Outliers can affect the mean and the standard deviation of a dataset, but they have little effect on the median, unless there are many of them or they are very extreme.
  - One measure of spread that is not significantly impacted by outliers is the interquartile range (IQR). The IQR is the difference between the third quartile (Q3) and the first quartile (Q1) of a dataset. It measures the spread of the middle 50% of the data values. Outliers can affect the range and the standard deviation of a dataset, but they have little effect on the IQR, unless there are many of them or they are very extreme.
  - As we are looking for MSE min, we still need to print out min values of MSE.

### Observation:

As we allows the algorithm to quite freely explore the parameters to have the lowest MSE. We can achieve MSE min by basically using very very high RPM which is not physically possible and recommended. However, the estimated MSE min is good for our study for further optimizing drilling parameters when we have controlled on the realistic ranges of drilling parameters.
