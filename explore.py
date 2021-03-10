import pandas as pd 
import os
import numpy
from time import sleep
import pickle

def get_datasets():
    """
    In datasets each dataset can either be in 1 directory or no directory - 
    a list is created of all files within
    and files grouped by the name of the directory
    """
    all = []
    subject = {}
    for root, dirs, files in os.walk("datasets"):
        for file in files:
            if file.endswith(".xls") or file.endswith(".xlsx"):
                f = os.path.join(root, file)
                all.append(f)
                spl = f.split('/')
                if len(spl) > 2:
                    dir = spl[1]
                else:
                    dir = "none"
                if dir in subject:
                    subject[dir].append(f)
                else:
                    subject[dir] = [f]    
    return all, subject

def count_stops():
    """
    Get amount and named of dictionaries with .stop at the end
    (can't be read)
    """
    count = 0
    entries = []
    for root, dirs, files in os.walk("datasets"):
            for file in files:
                if file.endswith(".stop"):
                    count += 1
                    entries.append(os.path.join(root, file))
    return count, entries

def has_nan(row):
    """
    Returns true if an iterable structures has a single NaN
    """
    for el in row:
        if pd.isna(el):
            return True
    return False

def all_nan(row):
    """
    Returns true if an iterable structure is all NaNs
    """
    for el in row:
        if not (pd.isna(el)):
            return False
    return True
    
def find_afghanistan(df):
    """
    Finds row and index for afghanistan-
    First country alphabetically which should sit on top of lists
    """
    col = 0 
    flag = True
    while col < len(df.axes[1]):
        rowCount = 1
        while rowCount < 50:
            x = df.loc[rowCount]
            if x[col] == 'Afghanistan':
                afloc = (col, rowCount)
                col = len(df.axes[1])
                break
            rowCount += 1
        col += 1
    return afloc

def countries_present(file):
    """
    Returns a dictionary of keys (countries in the sheet)
    mapped to values (fraction of possible boxes filled)
    """
    df = pd.read_excel(file)
    initcol, initrow = find_afghanistan(df)

    if all_nan(df.loc[initrow-1]):
        headings = df.loc[initrow-2]
    else:
        headings = df.loc[initrow-1]
    cols = []
    for index in range(1,len(headings)-1):
        if pd.isna(headings[index]):
            pass
        else:
            cols.append((headings[index], index))

    country_dict = {}
    end_countries = False
    x = initrow
    while not end_countries:
        row = df.loc[x]
        country = row[initcol]
        if country == 'World' or pd.isna(country):
            end_countries = True
        data = (0,0)
        for typ, index in cols:
            if pd.isna(row[index]) or not(any(char.isdigit() for char in str(row[index]))):
                data = (data[0],data[1]+1)
            else:
                data = (data[0] + 1, data[1] + 1)
                
        country_dict[country] = (data[0] / data[1])
        x += 1

    return country_dict
    
 
    
def combine_dictionaries(lst):
    """
    Take a list of dictionaries and combine them
    Give average,total, amount of zeros, min and max for each country
    """
    c = 0
    leng = len(lst)
    new_dict = {}

    ks = []
    for l in lst:
        ks = list(set(ks) | set(list(l.keys())))
    

    for key in ks:
        l = []
        for dict in lst:
            if key in dict:
                l.append(dict[key])
            else:
                l.append(0)
        new_dict[key] = (numpy.average(l), numpy.sum(l), len([x for x in l if x == 0]), numpy.min(l),numpy.max(l))
    
    return new_dict
   
def rank_countries_by_avg(dict, rev=True):
    return {k:v for k, v in sorted(dict.items(), key = lambda x : x[1][0], reverse= rev)}

def rank_countries_by_nonzero(dict, rev=False):
    return {k:v for k, v in sorted(dict.items(), key = lambda x : x[1][2], reverse= rev)}


if os.path.exists('alldictionary.pkl') and os.path.exists('catdictionary.pkl'):
    """
    If the dataset has already been saved
    """
    print("Datasets found, loading now")
    f1 = open('alldictionary.pkl','rb')
    all_dictionary = pickle.load(f1)
    f1.close()

    f2 = open('catdictionary.pkl','rb')
    cat_dictionary = pickle.load(f2)
    f2.close()

    print("Loaded")

    ranked = rank_countries_by_avg(all_dictionary)
    ks = list(ranked.keys())[0:20]
    print("Twenty Countries with highest average data")
    print("Country | Avg | Sum | # of 0s | min | max | appears in ")
    for k in ks:
        print(str(k) + "    " + str(ranked[k]))
    print("\n \n \n")

    ranked = rank_countries_by_nonzero(all_dictionary)
    ks = list(ranked.keys())[0:20]
    print("Twenty Countries with least missing data")
    print("Country | Avg | Sum | # of 0s | min | max | appears in ")
    for k in ks:
        print(str(k) + "    " + str(ranked[k]))
    print("\n \n \n")
    
    ranked = rank_countries_by_nonzero(cat_dictionary['ChildbirthAndEarlyChildhood'])
    ks = list(ranked.keys())[0:20]
    print("Twenty Countries with least missing data in Childbirth category")
    print("Country | Avg | Sum | # of 0s | min | max | appears in ")
    for k in ks:
        print(str(k) + "    " + str(ranked[k]))    
    print("\n \n \n")
else:
    """
    If the dataset needs to be generated
    """
    all_datasets , split_datasets = get_datasets()
    clist = []
    count = 0

    for dataset in all_datasets:
        try:
            clist.append(countries_present(dataset))
        except:
            os.rename(dataset, dataset + '.stop')
            print("Fixed Error Dataset")
            count += 1

    print("Completed dataset search for all")
    stopped, stopped_datasets = count_stops()
    print(str(stopped) + " datasets are marked as .stop so have not been read")
    print("Likely have an index page unfixed")
    print(str(count) + " datasets have been renamed to stop them")

    computed_dictionary = combine_dictionaries(clist)
    savefile = open('alldictionary.pkl','wb')
    pickle.dump(computed_dictionary,savefile)
    savefile.close()
    print("Saved")
    cat_dict = {}
    for category in split_datasets:
        clist = []
        for dataset in split_datasets[category]:
            try:
                clist.append(countries_present(dataset))
            except:
                pass
        combine_dict = combine_dictionaries(clist)
       
        cat_dict[category] = combine_dict
    print("Completed dataset search for category")
    savefile = open('catdictionary.pkl','wb')
    pickle.dump(cat_dict,savefile)
    savefile.close()
    print("Saved")