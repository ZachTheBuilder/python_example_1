'''
Author: Zach Rosson
Date: 4/19/18                                            
Description:
this program will scrape websites, save the soup, and then has a function that does both.
main will check if a html file has been made of the websites and if they are not there it
will call scrape_and_save to acomplish it

this program will now also  make a lol from a soup, check if a string can also be a int or float
, replace all flagged spots with an aprox of the prevous 5 and next 5 in the row, clean the data,
recalculate_annual_data after it has been cleaned, then it will all be used to clean_and_jsonify
a list of files and save them as .json


'''
import functools, requests, gzip, json, os.path
from bs4 import BeautifulSoup
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt 

def get_soup(url = None, fname = None, gzipped = False):
    '''this function takes a two strings and a boolen as its peramiters. the first string will be
    the url the second will be the file name and the last will be a bool on if it is zipped. it will
    then scrape the website according to which is None, Flase'''
    if fname:
        fp = open(fname)
        soup = BeautifulSoup(fp)
        return soup
    else:
        if url == None:
            raise RuntimeError("Either url or filename must be specified.")
        else:
            r = requests.get(url)
            if gzipped:
                unzipped = gzip.decompress(r.content)
                soup = BeautifulSoup(unzipped)
                return soup
            else:
                soup = BeautifulSoup(r.content)
                return soup
def save_soup(fname, soup):
    '''this function take two peramiters. the first one will be a string which 
    should be a filename. the second will be a soup object. this function will
    open the file and save that soup object to it in a textual rep of it'''
    fp = open(fname, 'w')
    fp.write(str(soup))
    fp.close()
def scrape_and_save():
    '''this fucntion takes no peramiters. it calls gt soup on three different files'''
    pcpn = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+pcpn+none+msum+5+01+F")
    mint = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+mint+none+mave+5+01+F")
    maxt = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+maxt+none+mave+5+01+F")
    save_soup('wrcc_pcpn.html', pcpn)
    save_soup('wrcc_mint.html', mint)
    save_soup('wrcc_maxt.html', maxt)
def is_num(str1):
    '''this function takes a string as its peramiter and cheks to see if it is a 
    int or float if it is return true if not false'''
    try:
        a = float(str1)
        return True
    except ValueError:
        return False
def load_lists(soup, flag):
    '''this function will take a soup and an int. the int is a flag that will be 
    replacing non-ints. this function will go thourgh the soup and collect the data
    to make the lol and then flag all non-ints in it.'''
    lol = []
    check = True
    for tr in soup.find_all('tr'):
        lst = []
        for td in tr.find_all('td'):
            if td.get_text() == 'z':
                lst.append(flag)
            elif is_num(td.get_text()):
                lst.append(float(td.get_text()))
        if lst == [] and check:
            check = False
        elif lst == []:
            break
        else:
            lol.append(lst)            
    lol2 = [list(i) for i in zip(*lol)]
    for i in range(len(lol2[0])):
        lol2[0][i] = int(lol2[0][i])
    return lol2
def replace_na(data, row, col, flag, pres=5):
    '''this function takes a lol and four ints. the first two ints are
    the posistions of where the flag is at. the third is the flag and 
    fourht is the amout of number to have after the decimal in the float 
    this funciton then finds the prevous 5 and next 5 adds them up and
    averages them out to find what the aprox would be at that spot'''
    '''
    lst = data[row][max(col-5, 0) :+6]
    while flag != lst:
        lst.remove(flag)
    return round(sum(lst)/len(lst), pres)
    
    '''
    sum = 0
    count = 0
    for c in range(len(data[row])):
        if data[row][col] == data[row][c]:
            if c == 0:
                i = 1
                chckr = 6
                for i in range(chckr):
                    if data[row][c+i] != flag:
                        sum += data[row][c+i]
                        count += 1
                break
            elif c == len(data[row])-1:
                j = 1
                chckl = 6
                for j in range(chckl):
                    if data[row][c-j] != flag:
                        sum += data[row][c-j]
                        count += 1
                break
            elif c > 4 and c < len(data[row])-4:
                i = 1
                chckr = 6
                for i in range(chckr):
                    if data[row][c+i] != flag:
                        sum += data[row][c+i]
                        count += 1
                j = 1
                chckl = 6
                for j in range(chckl):
                    if data[row][c-j] != flag:
                        sum += data[row][c-j]
                        count += 1
                break
            else:
                i = 1 
                chckr = 6
                for i in range(chckr):
                    if c+i < len(data[row]):
                        if data[row][c+i] != flag:
                            sum += data[row][c+i]
                            count += 1
                j = 1 
                chckl = 6
                for j in range(chckl):
                    if c-j >= 0:
                        if data[row][c-j] != flag:
                            sum += data[row][c-j]
                            count += 1
                break
    sum = round(sum, pres)
    avg = round(sum/count, pres)
    return avg
    
def clean_data(data, flag, pres):
    '''this function takes a lol and two ints. the first int is a flag and the second is
    the amout of numbers to have after the decimal in the float these two are just to be
    passed on to replace_na same with the lol'''
    for x in range(len(data)):
        for y in range(len(data[0])):
            if data[x][y] == flag:
                data[x][y] = replace_na(data, x, y, flag, pres)
                
def recalculate_annual_data(data, bol=False, pres=5):
    '''this funciton takes a lol, boolen, and an int.the program will find the average 
    of all the ints in the column adds them and averages them out. the boolen will determine
    the path it takes to complete it'''
    result = []
    avg = []
    lol = data[1:-1]
    temp = [[row[i] for row in lol] for i in range(len(lol[0]))]
    for r in range(len(temp)):
        sum = 0
        count = 0
        for c in range(len(temp[r])):
            sum += temp[r][c]
            count += 1
        sum = round(sum, pres)
        avg.append(round(sum/count, pres))
        result.append(sum)
    if bol:
        data[-1] = avg
    else:
        data[-1] = result
def clean_and_jsonify(fnames, flag, pres):
    '''this function takes a list of file names and two ints the first int is a flag the second
    is the amout of number to have after the decimal in the float. this function will then open
    each file individualy make it a soup, turn it into a lol, clean the data, recalculate_annual_data
    and then save it with the .json ending'''
    pcpn = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+pcpn+none+msum+5+01+F")
    mint = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+mint+none+mave+5+01+F")
    maxt = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+maxt+none+mave+5+01+F")
    save_soup('wrcc_pcpn.html', pcpn)
    save_soup('wrcc_mint.html', mint)
    save_soup('wrcc_maxt.html', maxt)
    for fname in fnames:
        if fname == 'wrcc_pcpn.html':
            soup = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+pcpn+none+msum+5+01+F")
            check = False
        if fname == 'wrcc_mint.html':
            soup = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+mint+none+mave+5+01+F")
            check = True
        if fname == 'wrcc_maxt.html':
            soup = get_soup("https://wrcc.dri.edu/WRCCWrappers.py?sodxtrmts+028815+por+por+maxt+none+mave+5+01+F")
            check = True
        data = load_lists(soup, flag)
        clean_data(data, flag, pres)
        recalculate_annual_data(data, check, pres)
        j_file = fname.replace('html', 'json')
        with open(j_file, 'w') as fp:
            json.dump(data, fp)
def get_panda(fname):
    ''' this function takes a string representing a filename as its sole argument.  The file
    contains ajson object representing a list of list. le.  Return a DataFrame that has the 
    same data as the list with row labels (index) that are the three-letter abbreviations for
    the months and the year and column labels (columns) that are integers representing years'''
    
    abv = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Ann']
    data = []
    with open(fname) as j_data:
        data = json.load(j_data)
    return DataFrame(data[1:], abv, data[0]) 
def get_stats(df):
    '''this function takes a DataFrame as its sole argument andreturns a new DataFrame 
    containing a statistical summary of the argument. Use these values for the return object's
    index: ['mean', 'sigma', 's', 'r']and the index from the argument for its columns. 
    Calculate the statistics and populate the DataFrame with them.  You may want to store
    them in a list of lists or np array and then pass that to the DataFrame constructor.'''
    col = df.index.values
    index = ['mean', 'sigma', 's', 'r']
    data = [[],[],[],[]]
    for r in range(len(df.index.values)):
        row_data = Series(df.loc[df.index.values[r]].values)
        data[0].append(np.mean(row_data))
        data[1].append(np.std(row_data, ddof=0))
        data[2].append(np.std(row_data, ddof=1))
        data[3].append(row_data.corr(Series(df.columns.values)))
    return DataFrame(data, index, col)
def print_stats(fname):
    '''this function takes a filename as its sole argument. Create a DataFrame from the data in 
    the file.  Print a DataFrame containing a statistical summary of that data.'''
    print('----- Statistics for '+fname+' -----\n')
    df = get_panda(fname)
    print(get_stats(df))
    print()
def smooth_data(df, precision=5):
    '''this function takes a DataFrameas its first argument and returns a DataFrame 
    with the same index and columns but each data point has been replaced with the 
    11-year average of the surrounding data including the data point itself.  The second 
    argument specifies a precision for each datum (number of decimal places) in the new 
    DataFrame and has a default value of 5.'''    
    #each data point will be replaced by an 11 year average of surrounding data inclusing itself
    data = df.values
    new_data = np.copy(data)
    
    for row in range(len(data)):
        for col in range(len(data[0])):
            lst = []
            if col-5 <= 0:
                lst = data[row][0 :col+6]
            elif col + 6 >= len(data[0]):
                lst = data[row][col-5 : len(data[0])]
            else:
                lst = data[row][col-5 :col+6]
            if len(lst) != 0:
                new_data[row][col] = round(sum(lst)/len(lst), precision)     
    return DataFrame(new_data, df.index.values, df.columns.values)   
def make_plot(fname, abv=None, precision=5):
    ''''''
    #get dataframe
    df = get_panda(fname)
    #smooth dataframe
    smooth_df = smooth_data(df, precision)
    #get dataframe values for both
    data = df.values
    sm_data= smooth_df.values
    #transpose both
    norm = np.transpose(data)
    smot = np.transpose(sm_data)
    #set them to a dataframe
    tran_df = DataFrame(norm, df.columns.values, df.index.values)
    tran_sm = DataFrame(smot, df.columns.values, df.index.values)
    
    if abv == None:
        '''plot every month as its own subplot no legend or y ticks make title name of 
        filename lable each subplot on the left with the 3letter abv of the month'''
        
        frame1 = tran_df
        frame2 = tran_sm
        abv2 = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Ann']
        p = frame1.plot(subplots=True, legend=None, color='r', yticks=[], title=fname) 
        for i in range(len(abv2)):
            p[i].set_ylabel(abv2[i])
        
        for x in range(len(abv2)):
            line = Series(sm_data[x], frame2.index.values)
            line.plot(ax=p[x]) 
    else:
        #plot both dataframes title is name of the file followed by a colon and the month string
        frame1 = tran_df
        frame2 = tran_sm
        abv = 'Jan'
        for x in range(len(tran_sm.columns.values)):
            if abv == tran_sm.columns.values[x]:
                line1 = Series(data[x], frame2.index.values)
                line2 = Series(sm_data[x], frame2.index.values)
                p = line1.plot(subplots=False, legend=abv, color='r', yticks= tran_df.index.values, title=fname+' '+abv)  
                line2.plot(ax=p)
                break 
        
def main():
    '''this program will scrape websites, save the soup, and then has a function that does both.
    main will check if a html file has been made of the websites and if they are not there it
    will call scrape_and_save to acomplish it
    
    this program will now also  make a lol from a soup, check if a string can also be a int or float
    , replace all flagged spots with an aprox of the prevous 5 and next 5 in the row, clean the data,
    recalculate_annual_data after it has been cleaned, then it will all be used to clean_and_jsonify
    a list of files and save them as .json'''
    if not os.path.isfile("wrcc_pcpn.html") or not os.path.isfile("wrcc_mint.html")or not os.path.isfile("wrcc_maxt.html"):
        print('---- scraping and saving ----')
        scrape_and_save()
    fnames = ['wrcc_pcpn.html',   'wrcc_mint.html', 'wrcc_maxt.html'] 
    clean_and_jsonify(fnames, -999, 2)
    for fname in fnames: 
        json_fname = fname.split('.')[0] + '.json' 
        print_stats(json_fname) 
        make_plot(json_fname, precision=2)
    plt.figure() 
    plt.show() 
    make_plot(fnames[0].split('.')[0] + '.json', 'Jan') 
    input('Enter to end:') 
    
if __name__ == '__main__':
    main()
