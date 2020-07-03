
pValue = 0.1; adjpValue = "none"; groupFlag = TRUE; consoleFlag = FALSE


reps <- 1000
sigvsNonSig <- data.table(anovaPValue=logical(), LSDPValue=logical(), TukeyPValue=logical(), scheffePValue = logical()) 
set.seed(12345)
for (i in 1:reps){
  x <- as.factor(rep(1:5,20))
  y <- rnorm(100,mean = 0,sd = 1)
  anovaResult <- aov(y~x)
  anovaPValue <- summary(anovaResult)[[1]][1,5] <= pValue
  LSDPValue <- all(agricolae::LSD.test(y = anovaResult, trt = "x", alpha = pValue, p.adj=adjpValue, group=groupFlag, main = NULL,console=consoleFlag)$groups$groups=="a")
  TukeyPValue <- all(agricolae::HSD.test(y = anovaResult, trt = "x", alpha = pValue, group=groupFlag, main = NULL,console=consoleFlag, unbalanced=TRUE)$groups$groups == "a")
  scheffePValue <- all(agricolae::scheffe.test(y= anovaResult, trt = "x", alpha = pValue, group=groupFlag, main = NULL, console=consoleFlag)$groups$groups=="a")
  all_PValue <- cbind(anovaPValue,LSDPValue,TukeyPValue,scheffePValue)
  sigvsNonSig <- rbind(sigvsNonSig,all_PValue)
}

table(sigvsNonSig$anovaPValue,sigvsNonSig$LSDPValue)
table(sigvsNonSig$anovaPValue,sigvsNonSig$TukeyPValue)
table(sigvsNonSig$anovaPValue,sigvsNonSig$scheffePValue)
