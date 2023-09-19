def write_data(json_file, data_index, output_file):
    import json
    import csv

    def retrieve(json_):
        # function to retrieve data from a json file
        file = open(json_, 'r')
        data = json.load(file)
        return data

    read_data = retrieve(json_file)[data_index]

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(read_data)


write_data("bat_data.json", "written_data", "final_bat_auction_data.csv")
