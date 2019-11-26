path = "C:/Users/samantas/Documents/MyLearning/MCMC/"
fileName = "data.csv"

# Declaration of Initial parameters;
startingRandomSeed = 12345
noofMCSimulation = 500000
sigmaAlpha = 1.0; sigmaBeta = 1.0
rhoAlphaBeta = 0.01
p = 10; q = 10;
# rand(InverseGamma(p,q),1)[1]

# Installing Packages;
# import Pkg
# Pkg.update()
# Pkg.add("CSV")
# Pkg.add("Distributions")
# Pkg.add("LinearAlgebra")
# Pkg.add("JuliaInterpreter")
# Pkg.add("GLM")
# Pkg.add("DataFrames")
# Pkg.add("Statistics")
# Pkg.add("Plots")
# Pkg.add("pyplot")


# Folder Structure;
inputPath = path * "Inputs/"
outputPath = path * "Outputs/"

# Calling Packages;
using Random, Distributions, CSV, LinearAlgebra, GLM, DataFrames, Statistics

# Reading data;
inputData = CSV.read(inputPath * fileName)
Y = convert(Array{Float64,1},inputData.One_SPI)
X = convert(Array{Float64,1},inputData.Rainfall)
xMin = 0; xSecondMin = quantile!(X, 0.25);noObs = length(Y)
inputData[:adjustedRainfall] = Base.log.(inputData[:Rainfall] .+ xSecondMin)
priorestimates = lm(@formula(One_SPI ~ adjustedRainfall), inputData)

# Prior estimates calculation based on linear-log model

using Dates, Distributed


# Likelihood(initialAlpha, initialBeta, initialLambda,1)
nworkers()
addprocs(4)
@everywhere include("C:/Users/samantas/Documents/MyLearning/MCMC/src/Code1.jl")
@everywhere using Random, Distributions, LinearAlgebra, GLM, DataFrames, Statistics, CSV
@everywhere sigmaAlpha = 1.0; @everywhere sigmaBeta = 1.0
@everywhere rhoAlphaBeta = 0.01;
@everywhere p = 10; @everywhere q = 10;
@everywhere path = "C:/Users/samantas/Documents/MyLearning/MCMC/"
@everywhere fileName = "data.csv"
@everywhere inputPath = path * "Inputs/"
@everywhere outputPath = path * "Outputs/"

@everywhere inputData = CSV.read(inputPath * fileName)
@everywhere Y = convert(Array{Float64,1},inputData.One_SPI)
@everywhere X = convert(Array{Float64,1},inputData.Rainfall)
@everywhere xMin = 0; @everywhere xSecondMin = quantile!(X, 0.25); @everywhere noObs = length(Y)
intAlpha = GLM.coef(priorestimates)[1]
intBeta = GLM.coef(priorestimates)[2]

@everywhere function f(no_of_simulation::Any, intalpha::Any, intBeta::Any, startingRandomSeed::Any)
    let
        global initialAlpha = intalpha;
        global initialBeta = intBeta;
        global initialLambda = rand(Uniform(xMin,xSecondMin),1)[1];
        global MCMCEstimates = DataFrame(iteration = Float64[],
                                Alpha=Float64[],Beta=Float64[],Lambda=Float64[],
                                phi=Float64[],tau=Float64[],L0=Float64[],L1=Float64[],
                                condition=Float64[]);
         # Likelihood() @sync @distributed
        for iter = 1:no_of_simulation
            # print(iter);
            # iter = 1;
            seed = startingRandomSeed * iter
            L0 = Likelihood(initialAlpha, initialBeta, initialLambda, seed)
            L1 = Likelihood(L0[2][1], L0[3][1], L0[4][1], seed)
            Random.seed!(seed)
            phi = rand(Uniform(0,1),1)[1]
            tau = Base.minimum([1,L1[1][1]/L0[1][1]])
            if((tau > phi) & (L0[3][1] > 0.0))
                initialAlpha = L0[2][1];initialBeta = L0[3][1];initialLambda = L0[4][1];condition = 1;
            else
                initialAlpha = initialAlpha; initialBeta = initialBeta;initialLambda = initialLambda;condition = 0;
            end
            MCMCEstimates = vcat(MCMCEstimates,
                            DataFrame(
                                    iteration = iter,
                                    Alpha=initialAlpha,Beta=initialBeta,Lambda=initialLambda,
                                    phi=phi,tau=tau,L0=L0[1][1],L1 = L1[1][1],
                                    condition=condition))
        end
    end
    MCMCEstimates
end

output = @spawnat 2 f(noofMCSimulation, intAlpha, intBeta, startingRandomSeed)
MCMCEstimates = fetch(output)
CSV.write(outputPath * "Output_" * Dates.format(Dates.now(), "yyyy-mm-dd HH_MM_SS") * ".csv", MCMCEstimates)
