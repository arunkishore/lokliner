import pandas as pd, numpy as np
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint


def apply_dbscan(location_points):
    '''

    :param location_points: get location points in format [ [lat,lng], [lat, lng] ]
    :return: location points in format [ [lat,lng], [lat, lng] ]
    '''

    # convert location point into panda Dataframe, add columns to dataframe [lat, lng]
    df = pd.DataFrame.from_records(location_points, columns=['lat', 'lng'])

    # further, convert them into list
    coords = df.as_matrix(columns=['lat', 'lng'])

    # converting locations into radians format
    kms_per_radian = 6371.0088

    # epsilon can very based on bound you want
    # epsilon and coordinates  get converted to radians,
    # because scikit-learn's haversine metric needs radian units
    bound = 0.01
    epsilon = bound / kms_per_radian

    # applying dbscan on the location_points
    # min_samples: minimum points in a cluster will be 1
    # using ball tree algorithm
    # haversine to calculate distance
    # coords (location points) will be converted to radian point
    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))

    # dbscan divided the points based on cluster
    cluster_labels = db.labels_

    # number of cluster dbscan have divided the points in coords
    num_clusters = len(set(cluster_labels))

    # converting clusters into pandas Series point
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])

    # The point nearest its center is perfectly suitable for representing the cluster
    # returning the point within it that is nearest to some reference point
    centermost_points = clusters.map(get_centermost_point)

    # for each element (i.e., cluster) in the series,
    # it gets the center-most point and
    # then assembles all these center-most points into a new series called centermost_points.
    lats, lons = zip(*centermost_points)
    print len(lats), len(lons)
    new_rep_list = []
    for i in range(0,len(lats)):
        new_rep_list.append([lats[i],lons[i]])


    return new_rep_list



def get_centermost_point(cluster):
    # calculates the centroid's coordinates
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)

    # Python's built-in min function to find the smallest member of the cluster in terms of distance to that centroid.
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)