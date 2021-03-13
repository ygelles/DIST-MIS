from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np


class Faddc:

    def __init__(self, n_cluster, feature_count, visualize=True):
        self.visualize = visualize
        self.n_clusters = n_cluster
        self.m_centroids = np.zeros((n_cluster, feature_count))
        self.m_count = np.zeros((n_cluster, 1))
        if visualize:
            axes = plt.gca()
            axes.set_xlim([-5, 5])
            axes.set_ylim([-5, 5])

    def mergeCentroids(self):
        # find pair with min distance...
        dist = euclidean_distances(self.m_centroids, self.m_centroids)
        dist = np.triu(dist, 1)
        dist[dist == 0] = np.nan

        try:
            c1, c2 = np.unravel_index(np.nanargmin(dist), np.array(dist).shape)
        except ValueError:  # first case scenario
            return (0, 1)

        self.m_centroids[c1] = ((self.m_centroids[c2] * self.m_count[c2]) + (self.m_centroids[c1] * self.m_count[c1])) \
                               / (self.m_count[c2] + self.m_count[c1])
        self.m_centroids[c2] = None
        self.m_count[c1] += self.m_count[c2]
        return (c2, c1)

    def faddcRule(self, newPoint):
        newCentroid, mergedCentroid = self.mergeCentroids()
        self.m_centroids[newCentroid] = newPoint
        self.m_count[newCentroid] = 1

    def fit(self, X):

        for x in X:

            self.faddcRule(x)
            if self.visualize:
                plt.scatter(x[0], x[1], color='blue')
                #plt.pause(0.03)
                cur_cluster = plt.scatter(self.m_centroids[:, 0], self.m_centroids[:, 1], color='green', s=self.m_count*4)
                plt.pause(1)
                cur_cluster.remove()


    def predict(self, X):
        y1_err = euclidean_distances(X, self.m_centroids)
        y1 = np.argmin(y1_err, axis=1)
        return (y1, y1_err)


def get_all_data():
    X, y = make_blobs(n_samples=500000, centers=1, n_features=1, center_box=(-10.0, 10.0), random_state=0)
    X_all = pd.DataFrame(X)
    X_all = X_all - X_all.mean()
    return X_all

def get_2d_data():
    X_all = get_all_data()
    samples = 1000
    dimen = 2
    X = X_all.sample(n=samples).reset_index(drop=True)
    for d in range(1, dimen):
        X2 = X_all.sample(n=samples).reset_index(drop=True).rename(columns={0:d})
        X = pd.concat([X, X2], axis=1)
    return X

X = get_2d_data()
#X.plot.scatter([0],[1])
X1 = (X / 4) + 2
X1 = X1.sample(X1.shape[0] // 10)


def plot_kmeans_solutions():

    kmeans = KMeans(n_clusters=2, random_state=0).fit(X.append(X1))
    centroids_df = pd.DataFrame(kmeans.cluster_centers_)
    labels_df = pd.DataFrame(kmeans.labels_)
    count_df = labels_df[0].value_counts()
    count_df = count_df.reset_index().sort_values('index')[0]
    plt.close()
    plt.scatter(X[0], X[1])
    plt.scatter(X1[0], X1[1])
    plt.scatter(centroids_df[0], centroids_df[1], s=count_df)
    plt.show()



def plot_faddc(visulaize=True):
    faddc = Faddc(n_cluster=4, feature_count=2, visualize=visulaize)
    faddc.fit(X.append(X1).values)
    centroids_df = pd.DataFrame(faddc.m_centroids)
    plt.close()

    plt.scatter(X[0], X[1])

    plt.scatter(X1[0], X1[1])

    plt.scatter(centroids_df[0], centroids_df[1], s=faddc.m_count)
    plt.show()


# plot_kmeans_solutions()
plot_faddc(visulaize=False)