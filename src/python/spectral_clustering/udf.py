import pandas as pd
import numpy as np
from datetime import datetime

from spectral_clustering.spectral_clustering import FinalCentralizedData, outputpath, groupByVar, clusterVars


def write_to_csv(OutPath, DataSet, FileName, ExtnofFile, TimeStampFlag, IndexFlag):
    if (TimeStampFlag == True):
        DataSet.to_csv(OutPath + '/' + FileName + '_' + datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.' + ExtnofFile, index = IndexFlag)
    else:
        DataSet.to_csv(OutPath + '/' + FileName +  '.' + ExtnofFile, index=IndexFlag)

def avg_fn(inputdf, groupbyvar, AvgVars):
    # AggregatedFigures = inputdf.groupby(groupbyvar,as_index=False).agg({AvgVars: [('WtAvgSP', wtavg(inputdf = inputdf,wtvar=WeightsVars))]})
    AggregatedFigures = inputdf.groupby(groupbyvar,as_index=False).agg({AvgVars: [('', lambda x: np.median(x))]})
    return AggregatedFigures

def renaming_vars(inputdf):
    inputdf.columns = ["".join(x) for x in inputdf.columns.ravel()]
    inputdf = inputdf.rename(columns=lambda x: x.rstrip("")).reset_index(drop=True)
    return inputdf

def df_merging_fn(LeftDF, RightDF, typeofJoin, LeftDFKeys, RightDFKeys):
    MergedDF = pd.merge(left = LeftDF, right = RightDF, how=typeofJoin, on=None, left_on=LeftDFKeys, right_on=RightDFKeys,
                        left_index=False, right_index=False, sort=True,suffixes=('_x', '_y'), copy=True, indicator=False, validate=None)
    return MergedDF

def get_affinity_matrix(coordinates, k):
    """
    Calculate affinity matrix based on input coordinates matrix and the numeber
    of nearest neighbours.

    Apply local scaling based on the k nearest neighbour
        References:
    https://papers.nips.cc/paper/2619-self-tuning-spectral-clustering.pdf
    """
    # calculate euclidian distance matrix
    dists = squareform(pdist(coordinates))

    # for each row, sort the distances ascendingly and take the index of the
    # k-th position (nearest neighbour)
    knn_distances = np.sort(dists, axis=0)[k]
    knn_distances = knn_distances[np.newaxis].T

    # calculate sigma_i * sigma_j
    local_scale = knn_distances.dot(knn_distances.T)

    affinity_matrix = dists * dists
    affinity_matrix = -affinity_matrix / local_scale
    # divide square distance matrix by local scale
    affinity_matrix[np.where(np.isnan(affinity_matrix))] = 0.0
    # apply exponential
    affinity_matrix = np.exp(affinity_matrix)
    np.fill_diagonal(affinity_matrix, 0)
    return affinity_matrix

def eigenDecomposition(A, plot, topK):
    """
    :param A: Affinity matrix
    :param plot: plots the sorted eigen values for visual inspection
    :return A tuple containing:
    - the optimal number of clusters by eigengap heuristic
    - all eigen values
    - all eigen vectors

    This method performs the eigen decomposition on a given affinity matrix,
    following the steps recommended in the paper:
    1. Construct the normalized affinity matrix: L = D−1/2ADˆ −1/2.
    2. Find the eigenvalues and their associated eigen vectors
    3. Identify the maximum gap which corresponds to the number of clusters
    by eigengap heuristic

    References:
    https://papers.nips.cc/paper/2619-self-tuning-spectral-clustering.pdf
    http://www.kyb.mpg.de/fileadmin/user_upload/files/publications/attachments/Luxburg07_tutorial_4488%5b0%5d.pdf
    """
    L = csgraph.laplacian(A, normed=True)
    n_components = A.shape[0]

    # LM parameter : Eigenvalues with largest magnitude (eigs, eigsh), that is, largest eigenvalues in
    # the euclidean norm of complex numbers.
    #     eigenvalues, eigenvectors = eigsh(L, k=n_components, which="LM", sigma=1.0, maxiter=5000)
    eigenvalues, eigenvectors = LA.eig(L)

    if plot:
        plt.title('Largest eigen values of input matrix')
        plt.scatter(np.arange(len(eigenvalues)), eigenvalues)
        plt.grid()

    # Identify the optimal number of clusters as the index corresponding
    # to the larger gap between eigen values
    index_largest_gap = np.argsort(np.diff(eigenvalues))[::-1][:topK]
    nb_clusters = index_largest_gap + 1

    return nb_clusters, eigenvalues, eigenvectors

def SpectralClustering(vars):
    # vars = clusterVars
    X = FinalCentralizedData[vars].values  # .reshape(-1, 1)

    affinity_matrix = get_affinity_matrix(X, k=10)
    k, eigenV, _ = eigenDecomposition(A=affinity_matrix, plot=False, topK=10)
    # print(f'Optimal number of clusters {k}')
    from sklearn.cluster import SpectralClustering
    if (k[0] != 1):
        clustering = SpectralClustering(n_clusters=k[0], assign_labels="discretize", random_state=12345).fit(X)
    else:
        clustering = SpectralClustering(n_clusters = k[1], assign_labels="discretize", random_state=12345).fit(X)

    ClustersOutput = pd.DataFrame({'Clusters': clustering.labels_})
    type(ClustersOutput)
    FinalOutput = pd.concat([FinalCentralizedData.loc[:,groupByVar+clusterVars].reset_index(drop=True), ClustersOutput.reset_index(drop=True)], sort=False, axis=1)
    write_to_csv(OutPath=outputpath, DataSet=FinalOutput, FileName='ClusterOutput', ExtnofFile='csv', TimeStampFlag=True, IndexFlag=False)