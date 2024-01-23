def query_restaurants(dataframe, query_params, default_city=None, max_results=10):
    """
    Query the restaurant dataset based on various tags.
    
    :param dataframe: Pandas DataFrame containing the restaurant data.
    :param query_params: Dictionary with keys as tags ('Cuisine', 'City', 'Name') 
                         and values as strings to query.
    :param default_city: Default city to use if no city is specified in query_params.
    :param max_results: Maximum number of results to return if the city is not specified.
    :return: Filtered DataFrame based on the query parameters.
    """
    filtered_df = dataframe

    # if query params isnt about cuisine, city, or name, return empty dataframe
    if not any(key in query_params for key in ['Cuisine Style', 'City', 'Name']):
        print('No results found for the given query.')

    # Apply city filter
    if 'City' in query_params and query_params['City']:
        filtered_df = filtered_df[filtered_df['City'].str.contains(query_params['City'], case=False, na=False)]
    elif default_city:
        filtered_df = filtered_df[filtered_df['City'] == default_city]

    # Apply other filters
    if 'Name' in query_params:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(query_params['Name'], case=False, na=False)]

    if 'Cuisine Style' in query_params:
        # filter the restaurants that have this cuisine in their Cuisine Style list
        filtered_df = filtered_df[filtered_df['Cuisine Style'].apply(lambda x: query_params['Cuisine Style'] in x)]
    else:
        # If no cuisine is specified, sort by rating
        filtered_df = filtered_df.sort_values(by='Rating', ascending=False)
    
    # if filtered_df is the same as the original df, then no filters were applied and no results were found
    print(filtered_df.shape[0])
    print(dataframe.shape[0])
    if filtered_df.shape[0] == dataframe.shape[0] or filtered_df.shape[0] == 0:
        print('No results found for the given query.')
    else:
        print('Found {} results.'.format(filtered_df.shape[0]))

    # return at most 3 results
    return filtered_df.head(2)


