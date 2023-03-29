import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import random
import math

def get_skills():
    return ['regular', 'premium', 'special']

def generate_coords(seed, n_phleb, n_order, n_catchment, polygon):

    size = n_phleb+n_order+n_catchment
    
    coords_df = pd.DataFrame()
    # bounds of geodata
    x_min, y_min, x_max, y_max = polygon.total_bounds
    points_x = []
    points_y = []

    i=0
    random.seed(seed)
    while i < size:
        # generate random data within the bounds
        point = Point(random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        if polygon.contains(point).any():
            points_x.append(point.x)
            points_y.append(point.y)
            i += 1
            
    coords_df['x'] = points_x
    coords_df['y'] = points_y

    # search for, remove and replace duplicates
    while (True in coords_df.duplicated(subset=['x','y'], keep='first').unique()): # while there are duplicates
        # remove duplicate coordinate pairs, only keeping first occurrence
        coords_df.drop_duplicates(subset=['x','y'], keep='first')
        n = size - len(coords_df)
        while j < n:
            point = Point(random.uniform(x_min, x_max), random.uniform(y_min, y_max))
            if polygon.contains(point).any():
                coords_df.append(pd.DataFrame([point.x, point.y], colums=['x', 'y']))
                j += 1

    print(f"Presence of duplicates: {True in coords_df.duplicated(subset=['x','y'], keep='first').unique()}")
    
    order_coords = coords_df[:n_order]
    phleb_home_coords = coords_df[n_order:n_order+n_phleb]
    catchment_coords = coords_df[n_order+n_phleb:]
    return (catchment_coords, phleb_home_coords, order_coords)

def create_catchment_df(seed, coords):
    df = pd.DataFrame()
    catchment_coords = coords[0]
    df['long'] = catchment_coords['x'].to_numpy()
    df['lat'] = catchment_coords['y'].to_numpy()
    df.to_csv(f"Simulated Data/catchment_data_{seed}.csv", index=False)
    return df

def create_phleb_df(seed, coords, n_phleb, ratio=None):
    # random generator 
    rng = np.random.default_rng(seed)

    df = pd.DataFrame()
    # start shift either at 6 or 7
    df['shift_start'] = rng.integers(6, 8, n_phleb)

    # start break 4 hours after of work
    df['break_start'] = df['shift_start'] + 4

    # shift ends after 8 hours 
    df['shift_end'] = df['shift_start'] + 8

    if ratio == None:
        # choose a category randomly
        df['skill_cat'] = rng.choice(get_skills(), n_phleb)
    else:
        n_regular = math.floor(ratio[0]*n_phleb)
        n_premium = math.floor(ratio[1]*n_phleb)
        print(n_regular)
        df['skill_cat'] = 'regular'
        df.loc[n_regular:,'skill_cat'] = 'premium'
        df.loc[n_regular+n_premium:,'skill_cat'] = 'special'
        # df['skill_cat'] = rng.choice(get_skills(), n_phleb, p=[ratio[0], ratio[1], ratio[3]])

    # cost of hiring
    phleb_cost_dict = {
        'regular': 800,
        'premium': 900,
        'special': 1000,
    }
    df['cost'] = df['skill_cat'].apply(lambda x:phleb_cost_dict.get(x))

    # one-hot encode expertise from category
    df = pd.get_dummies(data=df, prefix='expertise', columns=['skill_cat'])
    df.loc[df['expertise_special'] == 1, 'expertise_premium'] = 1
    df.loc[(df['expertise_special'] == 1) | (df['expertise_premium'] == 1), 'expertise_regular'] = 1 
    
    # carrying capacity
    df['capacity'] = 20 

    # service rating
    df['service_rating'] = rng.lognormal(mean=4.5, sigma=0.1, size=n_phleb)
    df['service_rating'] = df['service_rating'] / df['service_rating'].max() *5.0 # scale to range of 0.0 to 5.0
    df['service_rating'] = df['service_rating'].round(decimals=1)

    # coordinates of phlebo's home
    phleb_home_coords = coords[1]
    df['long'] = phleb_home_coords['x'].to_numpy()
    df['lat'] = phleb_home_coords['y'].to_numpy()

    # gender, male = 0, female = 1
    df['gender'] = rng.choice(a=[0,1], size=n_phleb, p=[0.7, 0.3]) # 70% of phlebotomists are males
    
    # set phleb id
    df['phleb_id'] = df.index

    # df.to_csv(f"Simulated Data/phleb_data_{seed}.csv", index=False)
    print(df)
    return df

def create_orders_df(seed, coords, n_order, ratio=None):
    # random generator 
    rng = np.random.default_rng(seed) 

    df = pd.DataFrame()

    # array of hours to choose from
    hours = np.arange(6,15) # orders start from 6am to 2pm
    # probability of each hour being chosen
    p_hour = np.array([0.6, 0.6, 0.6, 0.6, 0.6, 0.4, 0.4, 0.4, 0.4])
    # the probabilities are scaled so that they sum to 1
    p_hour /= p_hour.sum()
    df['order_start'] = rng.choice(hours, size=n_order, p=p_hour)

    # generate number of services chosen
    df['num_services'] =  rng.integers(1, len(get_skills())+1, n_order) # each order must have at least 1 skill
    if ratio == None:
        # randomly choose skills from list of skills based
        df['services'] = df.num_services.apply(lambda x: str(rng.choice(get_skills(), x, replace=False, shuffle=True))[1:-1]).str.replace("'",'') 
    else: 
        total_num_services = df['num_services'].sum()
        services_df = pd.DataFrame(index=range(total_num_services), columns=['service'])
        services_df['service'] = 'regular'
        n_regular = math.floor(ratio[0]*total_num_services)
        n_premium = math.floor(ratio[1]*total_num_services)
        services_df.loc[n_regular:,'service'] = 'premium'
        services_df.loc[n_regular+n_premium:,'service'] = 'special'
        for index, row in df.iterrows():
            num_services = row['num_services']
            for i in range(num_services):
                index_chosen = rng.choice(services_df.index.to_list(), size=1, replace=False)[0]
                service_chosen = services_df.loc[index_chosen, 'service']
                if i == 0:
                    df.loc[index,'services'] = service_chosen
                    # row['services'] = service_chosen
                else:
                    df.loc[index,'services'] += f" {service_chosen}"
                    # row['services'] += service_chosen
                services_df.drop(index=index_chosen, inplace=True)

    # one-hot encoded columns
    dummies = df['services'].str.get_dummies(sep=" ").add_prefix('service_')
    # join df with one-hot encoded columns
    df = pd.concat([df, dummies], axis=1)

    # calculate order duration and price
    service_duration_dict = {
    'regular': 15,
    'premium': 15,
    'special': 15,
    }

    service_pricing_dict = {
        'regular': 200,
        'premium': 300,
        'special': 400,
    }
    df['duration'] = 0 # initialise column
    df['price'] = 0 # initialise column
    for skill in get_skills():
        df['duration'] += service_duration_dict.get(skill) * df[f"service_{skill}"]
        df['price'] += service_pricing_dict[skill] * df[f"service_{skill}"]

    # buffer time between 10 and 15mins
    df['buffer'] = rng.integers(10, 16, n_order)

    df['capacity_needed'] = df['num_services']
    
    # coordinates
    order_coords = coords[2]
    df['long'] = order_coords['x'].to_numpy()
    df['lat'] = order_coords['y'].to_numpy()

    df['order_id'] = df.index

    # gender, male = 0, female = 1
    df['requested_female'] = rng.choice(a=[0,1], size=n_order, p=[0.8,0.2]) 
  
    df.drop(['num_services', 'services'], inplace=True, axis=1)
    print(df)
    # df.to_csv(f"Simulated Data/order_data_{seed}.csv", index=False)
    return df

if __name__ == "__main__":
    polygon = gpd.read_file("Simulation\Gurugram_sample_Polygon.geojson")
    n_phleb = 10
    n_catchment = 0
    n_order = 10
    seed = 1
    coords = generate_coords(seed, n_phleb, n_order, n_catchment, polygon)
    catchment_df = create_catchment_df(seed, coords)
    phleb_df = create_phleb_df(seed, coords, n_phleb, [0.8, 0.1, 0.1])
    order_df = create_orders_df(seed, coords, n_order, [0.8, 0.1, 0.1])