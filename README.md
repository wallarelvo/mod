# mod
Machine learning and data analysis for **m**obility **o**n **d**emand

## Feature Extraction
### Using Open Street Maps
1. Update the polygonal area in the `nyc_poly` variable in `scripts/common.py`
2. Run `python scripts/create_query.py` to print the query for the OSM
data
3. Download the OSM data from `http://overpass-api.de/query_form.html`
using the query created from the command above
4. Run `python scripts/create_osm_graph.py` to generate the pickled python
graph
5. Filter the data file to only include the appropriate data points using
`python scripts/filter_data_file.py`
6. Run `python scripts/create_data_files.py` to create the CSV files used
for running the mobility on demand algorithms

### Using Pre-generated Graphs
1. TODO

## Data Analysis
1. Run `python scripts/load_metrics.py` to generate the DataFrame for the
performance metrics generated by the mobility on demand algorithms
2. Run `python scripts/plot_probs.py` to create plots and geo-plots for the
pickup-dropoff probabilities
3. Run `python scripts/plot_metrics.py` to create plots describing how well
the mobility on demands algorithms performed
