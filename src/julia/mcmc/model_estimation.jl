path = "C:/Users/samantas/Documents/MyLearning/MCMC/"
fileName = "data.csv"

# Declaration of Initial parameters;
startingRandomSeed = 12345
noofMCSimulation = 50 #500000
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

# Prior estimates calculation based on linear-log model
priorestimates = lm(@formula(One_SPI ~ adjustedRainfall), inputData)

# Generating Distributions;
function generatingBVN( noVars::Any,
                        m1::Any, s1::Any,
                        m2::Any, s2::Any,
                        rho::Any,
                        rs::Any,
                        p::Any, q::Any)
  Random.seed!(rs)
  alpha = rand(Normal(m1,s1),noVars)
  beta =  rand(Normal((m2 + (s2/s1) * rho * (alpha[1] - m1)), sqrt((1 - rho^2)*s2^2)),noVars)
  lambda = rand(Uniform(xMin, xSecondMin),noVars)
  errorVar = rand(InverseGamma(p,q),noVars)

  alpha, beta, lambda, errorVar
end

function Likelihood(alpha_t_1::Any,beta_t_1::Any, lambda_t::Any, randomSeed::Any)
    # alpha_t_1 = initialAlpha; beta_t_1 = initialBeta; lambda_t = initialLambda; randomSeed = 1;
    alpha_t, beta_t, lambda_t, sigmaSquareE = generatingBVN(1,initialAlpha,sigmaAlpha,initialBeta,sigmaBeta,rhoAlphaBeta,randomSeed, p, q)
    # generatingBVN(n=1,m1=muAlpha,s1=sigmaAlpha,m2=muBeta,s2=sigmaBeta,rho=rhoAlphaBeta,rs = randomSeed)

    ERROR = Y - repeat(alpha_t,noObs) - repeat(beta_t,noObs) .* Base.log.(repeat(lambda_t,noObs) + X)
    ESS = LinearAlgebra.dot(ERROR,ERROR)

    postLikelihood =
    [sigmaSquareE[1]^(-0.5 * (noObs + p + 2)) *
    exp(-(ESS + q)./(2 * sigmaSquareE)[1]) *
    (
        exp(-(((alpha_t[1] - alpha_t_1)/sigmaAlpha)^2 + ((beta_t[1] - beta_t_1)/sigmaBeta)^2 -
                2 * rhoAlphaBeta *  ((alpha_t[1] - alpha_t_1)/sigmaAlpha) * ((beta_t[1] - beta_t_1)/sigmaBeta))/(2*(1-rhoAlphaBeta^2))[1]
            )
        + lambda_t[1]
    )]

    postLikelihood, alpha_t, beta_t, lambda_t
end
# Likelihood(initialAlpha, initialBeta, initialLambda,1)

let
    global initialAlpha = GLM.coef(priorestimates)[1];
    global initialBeta = GLM.coef(priorestimates)[2];
    global initialLambda = rand(Uniform(xMin,xSecondMin),1)[1];
    global MCMCEstimates = DataFrame(iteration = Float64[],
                            Alpha=Float64[],Beta=Float64[],Lambda=Float64[],
                            phi=Float64[],tau=Float64[],L0=Float64[],L1=Float64[],
                            condition=Float64[]);

    for iter = 1:noofMCSimulation
        # print(iter);
        seed = startingRandomSeed * iter
        L0 = Likelihood(initialAlpha, initialBeta, initialLambda, seed)
        L1 = Likelihood(L0[2][1], L0[3][1], L0[4][1], seed)
        Random.seed!(seed)
        phi = rand(Uniform(0,1),1)[1]
        tau = Base.minimum([1,L1[1][1]/L0[1][1]])
        if(tau > phi)
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

CSV.write(outputPath * "output.csv", MCMCEstimates)

# using Plots
# pyplot()
# GAIPS7551E
#
# X =
# histogram(X)
