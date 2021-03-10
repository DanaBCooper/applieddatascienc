This repository has the datasets from UNICEF gender equality, dictionaries of the results and explore.py

Some datasets have a suffix '.stop' - this is just a trivial investigation, any with index
pages or issues that caused issues have been taken out of the equation temporarily.
Removing the .stop and dictionary files will cause the program to recalculate


Each dataset has the list of countries pulled and an estimate made of how filled it is
Each cell with a heading is a category, and the score for each country 
in each dataset is filled categories / total categories


These scores have been collated into 2 dictionaries
Dictionaries:
    alldictionary.pkl - A dictionary of keys (Countries) -> values (avg, sum, number empty, min, max) of score

    catdictionary.pkl - A dictionary of key (categories) -> values (dictionary for datasets in that 
    category). Each of those is same form as alldictionary.pkl.

Deleting the dictionaries will get the program to recompute (doesn't take long)
To get stats for a specific category, make a folder in datasets and put all the datasets you want
in the folder w/ the name of the category and recalculate
Then you can access catdictionary[category] to get your numbers.
