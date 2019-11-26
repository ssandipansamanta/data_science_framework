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
