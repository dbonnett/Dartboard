Vision: 
1) make a probability of winning graph based on how many darts left and current score. Start with 1 dart left (bullseye and 50 - score will have prob of 1, everywhere else prob of 0) (also, if already hit 50, prob everywhere is 1)
* intersect this with shot probability dist and optimize for coordinates. 

2) How to find best shot with 2 darts left? We want to maximize probability of winning with 3rd dart. Take each possible shot and calculate probability of all remaining outcomes. 
This means that to find the best shot 

Starting fresh - given a prob dist we can definitely calculate the prob of winning given score after 2 darts. 
The probability of winning based on where we aim with the second dart is the sum of all probabilities of landing in 