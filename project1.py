# si 201 - project 1 (sample superstore)
# author: Kamilah Sandoval
# umid: 59979502
# email: kamisand@umich.edu
# collaborators: none
# i used genai for explaining certain concepts from class, asking if i could use certain functions/ clarifying it will do what i want it to do,aksing it for clarity when I would get errors and my code would not run.

######################################################################
# what my whole project does
######################################################################
# STEP 1: read the dataset file (sample superstore.csv)
# STEP 2: clean the data (remove spaces, turn text numbers into real numbers)
# STEP 3: make two calculations:
#         (1) total / average / % standard class for every region × segment
#         (2) total / average for every category × sub-category
# STEP 4: write those results into two new csv files inside a folder named "results"

# function for eevry step and  main() runs them in order
######################################################################

import csv  # lets us open and read/write .csv files
import os   # lets us access my computer stuff

######################################################################
# SECTION 1: READ THE CSV FILE
######################################################################
# this fxn opens csv file and reads it
# every line from the csv file becomes a small "dictionary"
# (dictionary: data type that stores pairs like:
    #   "key" : "value"  → example:  {"Region":"West","Sales":"261.96"} )
    # the column headers (Region, Segment, Sales, etc) become the KEYS
    # the actual data in each row become the VALUES
        # this makes it easy to look up any piece of data later by its name
######################################################################

def read_csv(path_to_csv):
    # will call this fxn w ("SampleSuperstore.csv") as the parameter later btw
    

    # input: csv file name
    # output: a list that will hold one dictionary per row in the csv file

    rows = []  # start with an empty list that will store all row dictionaries

    # "with open()"  opens the file
    # when we reach the end of the "with" block, it automatically closes the file
    # "newline=''" prevents blank lines between rows when reading csv files
    # "encoding='utf-8'" lets us read all letters and special characters correctly
    with open(path_to_csv, newline='', encoding='utf-8') as f:
        # f is just a short nickname for "file".
        # csv.DictReader(f) reads the file and automatically uses the first row
        # (the headers) as the keys for each dictionary.
        reader = csv.DictReader(f)

        
        # going thru row. each row is a dictionary like {"Region":"West","Segment":"Consumer","Sales":"261.96"}
        for row in reader:
            # dict(row) makes sure the object is a normal dictionary type
            rows.append(dict(row))

    # returning rows sends that finished list full of all row dicts 
    return rows


######################################################################
# section 2: clean / prepare the data
######################################################################
# why we clean:
# - remove extra spaces from words (like " West " → "West")
# - convert the "Sales" column from text to a number so we can add/average it
# - keep only rows that have all the columns we need
######################################################################

# this helper fxn tries to turn text like "261.96" into a real number 261.96
def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None  # if it fails, return None (means "nothing" or "missing")

def clean_data(rows):
    cleaned = []  # new list to store cleaned rows

    # loop through each row dictionary in the list
    for row in rows:
        d = {}  # new empty dictionary to store cleaned values for this row

        # go through every key (column name) and value (cell data)
        for key, value in row.items():  # .items() lets me loop through both the column name (key) and its cell value
            # isinstance(value, str) checks if the value is a string
            if isinstance(value, str):
                d[key] = value.strip()  # .strip() removes spaces before/after text
            else:
                d[key] = value  # if it's not a string, keep it the same

        # convert the text "Sales" value into a float number
        # .get("Sales")  gets the value even if the key is missing
        d["Sales"] = to_float(d.get("Sales"))

        # make sure all important columns exist and are not empty
        needed_values = [
            d.get("Ship Mode"),
            d.get("Segment"),
            d.get("Region"),
            d.get("Category"),
            d.get("Sub-Category"),
            d.get("Sales"),
        ]

        # check if everything is filled
        has_everything = True
        for v in needed_values:
            if v is None or v == "":
                has_everything = False

        # only keep rows that have all needed information
        if has_everything:
            cleaned.append(d)

    return cleaned  # send back the cleaned list


######################################################################
# section 3: calculation 1 (region × segment + % standard class)
######################################################################
# what this does:
# - groups the cleaned data by region and segment
# - adds up total sales for each group
# - calculates the average sales per order
# - counts how many of those orders used "Standard Class" shipping
# - turns that count into a percentage
######################################################################

def calc_region_segment(rows, target_ship_mode="Standard Class"):
    # dictionaries that will store the totals and counts for each group
    sums = {}          # (region, segment) -> total sales amount
    counts = {}        # (region, segment) -> how many rows (orders)
    samples = {}       # (region, segment) -> list of sales numbers
    target_counts = {} # (region, segment) -> how many orders used the target ship mode

    # loop through each cleaned row of data
    for row in rows:
        region = row.get("Region")          # get region from the row
        segment = row.get("Segment")        # get customer segment
        ship_mode = row.get("Ship Mode")    # get shipping type
        sales = row.get("Sales")            # get the sales number
        key = (region, segment)             # make a tuple like ("West","Consumer")

        # if this group (region, segment) has not been seen yet, create empty boxes
        if key not in sums:
            sums[key] = 0.0
            counts[key] = 0
            samples[key] = []
            target_counts[key] = 0

        # add this row’s sales to the total
        if sales is not None:
            sums[key] = sums[key] + sales   # add sales to total
            samples[key].append(sales)      # also keep it in the list for averaging

        counts[key] = counts[key] + 1       # increase the number of orders by 1

        # check if this order used the target ship mode (standard class)
        if isinstance(ship_mode, str) and ship_mode.strip().lower() == target_ship_mode.strip().lower():
            target_counts[key] = target_counts[key] + 1

    # now build a new result dictionary with totals, averages, and percentages
    result = {}
    for key in sums:
        total = sums[key]  # total sales for this group
        n = counts.get(key, 0)  # how many orders
        sales_list = samples.get(key, [])
        target_n = target_counts.get(key, 0)  # how many used standard class

        # average = total of numbers ÷ how many numbers
        if len(sales_list) > 0:
            avg = sum(sales_list) / float(len(sales_list))
        else:
            avg = 0.0

        # percent = (count of target / total count) × 100
        if n > 0:
            pct = (target_n / float(n)) * 100.0
        else:
            pct = 0.0

        # store final results for this (region, segment)
        result[key] = {
            "total_sales": round(total, 2),
            "avg_sales_per_order": round(avg, 2),
            "pct_orders_target_ship_mode": round(pct, 2),
        }

    return result  # send back the summary dictionary


######################################################################
# section 4: calculation 2 (category × sub-category)
######################################################################
# what this does:
# - groups data by product category and sub-category
# - adds up total sales and calculates the average per order
######################################################################

def calc_category_sub(rows):
    sums = {}     # (category, subcategory) -> total sales
    counts = {}   # how many orders in that group
    samples = {}  # list of all sales amounts for that group

    for row in rows:
        cat = row.get("Category")
        sub = row.get("Sub-Category")
        sales = row.get("Sales")
        key = (cat, sub)

        if key not in sums:
            sums[key] = 0.0
            counts[key] = 0
            samples[key] = []

        if sales is not None:
            sums[key] = sums[key] + sales
            samples[key].append(sales)

        counts[key] = counts[key] + 1

    result = {}
    for key in sums:
        total = sums[key]
        sample_list = samples.get(key, [])
        if len(sample_list) > 0:
            avg = sum(sample_list) / float(len(sample_list))
        else:
            avg = 0.0

        result[key] = {
            "total_sales": round(total, 2),
            "avg_sales_per_order": round(avg, 2),
        }

    return result


######################################################################
# section 5: write the results into new csv files
######################################################################
# what this does:
# - makes a "results" folder if needed (os.makedirs)
# - writes new csv files with the calculated data
######################################################################

def write_region_segment_csv(results_dict, out_path):
    folder = os.path.dirname(out_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)  # create folder if it doesn’t exist yet

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)  # create a csv writer object
        w.writerow(["region", "segment", "total_sales", "avg_sales_per_order", "pct_orders_target_ship_mode"])
        for (region, segment) in sorted(results_dict.keys()):
            metrics = results_dict[(region, segment)]
            w.writerow([region, segment,
                        metrics["total_sales"],
                        metrics["avg_sales_per_order"],
                        metrics["pct_orders_target_ship_mode"]])

def write_category_sub_csv(results_dict, out_path):
    folder = os.path.dirname(out_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "sub_category", "total_sales", "avg_sales_per_order"])
        for (cat, sub) in sorted(results_dict.keys()):
            metrics = results_dict[(cat, sub)]
            w.writerow([cat, sub,
                        metrics["total_sales"],
                        metrics["avg_sales_per_order"]])


######################################################################
# section 6: main program (runs everything)
######################################################################
# what this function does:
# 1. reads csv
# 2. cleans data
# 3. does calc 1 and saves result
# 4. does calc 2 and saves result
######################################################################

def main():
    csv_name = os.path.join(os.path.dirname(__file__), "SampleSuperstore.csv") # used gen ai to help me since i was only able to use my perosnal files
    print("reading:", csv_name)
    raw_rows = read_csv(csv_name)  # call read_csv and save the returned list

    print("rows read:", len(raw_rows))  # show how many rows were read
    if len(raw_rows) == 0:
        print("file looks empty, check your folder name and file path")
        return  # stop if no data

    print("cleaning data...")
    cleaned_rows = clean_data(raw_rows)  # clean the data
    print("rows kept after cleaning:", len(cleaned_rows))

    print("doing calculation 1 (region × segment)...")
    calc1 = calc_region_segment(cleaned_rows, target_ship_mode="Standard Class")
    write_region_segment_csv(calc1, "results/region_segment_summary.csv")
    print("wrote: results/region_segment_summary.csv")

    print("doing calculation 2 (category × sub-category)...")
    calc2 = calc_category_sub(cleaned_rows)
    write_category_sub_csv(calc2, "results/category_sub_summary.csv")
    print("wrote: results/category_sub_summary.csv")

    print("All done! Results are in the results folder.")


######################################################################
# SECTION 7: MINI TESTS
######################################################################

# this function just returns 4 fake data rows (each row is a dictionary)
def _mini_rows():
    return [
        {"Ship Mode": "Standard Class", "Segment": "Consumer",
         "Region": "West", "Category": "Furniture",
         "Sub-Category": "Chairs", "Sales": 100.0},

        {"Ship Mode": "Second Class", "Segment": "Consumer",
         "Region": "West", "Category": "Furniture",
         "Sub-Category": "Tables", "Sales": 200.0},

        {"Ship Mode": "Standard Class", "Segment": "Corporate",
         "Region": "West", "Category": "Technology",
         "Sub-Category": "Phones", "Sales": 300.0},

        {"Ship Mode": "Same Day", "Segment": "Home Office",
         "Region": "Central", "Category": "Office Supplies",
         "Sub-Category": "Binders", "Sales": 50.0}
    ]


# actually testing fake data
def run_mini_tests():
    print("\nstarting my mini tests now...")

    # get my small fake dataset
    rows = _mini_rows()

    # call the first calculation using my fake data
    print("\n--- testing calc_region_segment ---")
    c1 = calc_region_segment(rows, target_ship_mode="Standard Class")

    # print a few of the results from calc_region_segment
    for group, metrics in c1.items():
        print("region and segment:", group, "→", metrics)

    # call the second calculation using the same fake data
    print("\n--- testing calc_category_sub ---")
    c2 = calc_category_sub(rows)

    # print a few of the results from calc_category_sub
    for group, metrics in c2.items():
        print("category and sub-category:", group, "→", metrics)

    print("\nmini tests finished. if the printed numbers look reasonable, "
          "then the main program should work correctly on the big csv.\n")



######################################################################
# section 8: choose what to run
######################################################################
# change run_tests_first to True if you want to see mini tests first
######################################################################

if __name__ == "__main__":
    run_tests_first = False
    if run_tests_first:
        run_mini_tests()
    else:
        main()
