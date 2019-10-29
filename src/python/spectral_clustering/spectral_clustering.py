from spectral_clustering.udf import avg_fn, renaming_vars, df_merging_fn, SpectralClustering
import pandas as pd

path = 'C:/Upcoming/DBSchemaExplore/'
groupByVar = ['Zone']
kpi = ['SPI_1','SPI_2','SPI_3']
clusterVars = ['SPI_1', 'SPI_2']
inputdataset = 'Test.csv'

# Don't need to change any thing below
# ====================================
inputpath = path + 'Inputs/'
outputpath = path + 'Outputs/'
codepath = path + 'src/python/'

exec(open(codepath + "RequiredPackages.py").read(), globals())
exec(open(codepath + "UserDefinedFn.py").read(), globals())
rawData = pd.read_csv(inputpath + inputdataset)

FinalCentralizedData = avg_fn(inputdf = rawData, groupbyvar = groupByVar, AvgVars=kpi[0]).reset_index(drop=True)
FinalCentralizedData = renaming_vars(FinalCentralizedData)

for i in range(1,len(kpi)):
    AvgValue = avg_fn(inputdf = rawData, groupbyvar = groupByVar, AvgVars=kpi[i]).reset_index(drop=True)
    AvgValue = renaming_vars(AvgValue)
    FinalCentralizedData = df_merging_fn(LeftDF = FinalCentralizedData, RightDF = AvgValue, typeofJoin ='left', LeftDFKeys = groupByVar, RightDFKeys = groupByVar)

# Running Spectral Clustering;
SpectralClustering(clusterVars)


