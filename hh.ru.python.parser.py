#!/usr/bin/python
# -*- coding:utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import hashlib
import pickle
import os
from tkinter import *
from tkinter import ttk

isDebug = False
# file for storing the current results
dumpfile = "PyJob.dump"


def log(r):
    if isDebug:
        r.printres()
        print("_________________\n")

# main settings dictionary
settings = {
    'hh.ru':{
        "url":'https://krasnoyarsk.hh.ru/search/vacancy?clusters=true&area=54&enable_snippets=true&text=python',
        "outer_block":("div",{'data-qa':"vacancy-serp__vacancy"}),
        "labels":("div", {"class":"search-item-name"}),
        "salaries":("div",{"data-qa":"vacancy-serp__vacancy-compensation"}),
        "urls":("a",{"data-qa":"vacancy-serp__vacancy-title"}),
        "descs":("div", {"data-qa":"vacancy-serp__vacancy_snippet_responsibility"}),
        "reqs": ("div",{"data-qa":"vacancy-serp__vacancy_snippet_requirement"}),
        "companies":("", {"data-qa":"vacancy-serp__vacancy-employer"}),
        "dates":("span", {"data-qa":"vacancy-serp__vacancy-date"}),
        },
    }


class result:
    url=""
    label=""
    salary=""
    desc=""
    date=""
    company=""
    uid = ""

    def __init__(self):
        return

    def setvalue(self,u,l,desc,date,comp,s="unknown"):
        self.url = u
        self.label = l
        self.salary=s
        self.desc = desc
        self.date = date
        self.company = comp

    def printreshtml(self):
        print('<a href="' + self.url + '"' + self.label + ' ' + self.salary + '</a><br><p>' + self.desc + " " + self.company + " " + self.date + "</p>")

    def printres(self):
        print(self.label + " " + self.salary + " " + self.desc + " " + self.date + "\r\n" + self.company + " " + self.url)

    def setmd5(self):
        self.uid = hashlib.md5(self.desc.encode('utf8')).hexdigest()


def deserialize(dfile):
    with open(dfile,'rb') as f:
        return pickle.load(f)


def serialize(results, tfile):
    # dump to file
    if not os.path.exists(tfile):
        with open(tfile, "wb") as f:
            pass
        with open(tfile,'r+b') as f:
            todump = []
            for i in results:
                todump.append(i)
            print(todump)
            pickle.dump(todump,f)


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(key=lambda t: int(t[0]), reverse=reverse)
    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    # reverse sort next time
    tv.heading(col, command=lambda: \
               treeview_sort_column(tv, col, not reverse))

def copy(event,root,string):
    root.clipboard_clear()
    root.clipboard_append(string)
    pass

def rightclick(event):
    contextMenu=Menu(root, tearoff=0)
    # select row under mouse
    iid = tree.identify_row(event.y)
    index = int(iid.replace("I",""),base=16) - 1
    string = ""
    contextMenu.add_command(label="Copy row", command=lambda: copy(event,root,string))
    contextMenu.add_command(label="Copy link", command=lambda: copy(event,root,string.split(" ")[-1]))
    if iid:
        # mouse pointer over item
        tree.selection_set(iid)
        contextMenu.post(event.x_root, event.y_root)
        for item in tree.get_children():
            if tree.item(item,"text") in iid:
                values = tree.item(item, "values")
                string = " ".join(values)



if __name__=='__main__':
    oldresults = []

    if os.path.exists(dumpfile):
         oldresults = deserialize(dumpfile)

    #print(len(oldresults))

    results = []

    # hh
    ipage=0
    html = urlopen(settings['hh.ru']['url'] + "&page={0}".format(ipage))
    bsObj = BeautifulSoup(html.read(),"html.parser")
    vacancies = bsObj.findAll(settings['hh.ru']['outer_block'][0],settings['hh.ru']['outer_block'][1]) # outer block

    while len(vacancies) > 0:
        for i,item in enumerate(vacancies):
            r=result()
            tempObj = BeautifulSoup(str(item),"html.parser")

            labels = tempObj.find(settings['hh.ru']['labels'][0],settings['hh.ru']['labels'][1])
            r.label=labels.get_text()

            salaries = tempObj.find(settings['hh.ru']['salaries'][0],settings['hh.ru']['salaries'][1])
            getsalaries = "unknown"
            if salaries != None:
                getsalaries = salaries.get_text()
            r.salary = getsalaries

            urls = tempObj.find(settings['hh.ru']['urls'][0],settings['hh.ru']['urls'][1])
            r.url = urls['href']

            descs = tempObj.find(settings['hh.ru']['descs'][0], settings['hh.ru']['descs'][1])
            r.desc = descs.get_text()

            reqs = tempObj.find(settings['hh.ru']['reqs'][0], settings['hh.ru']['reqs'][1])
            r.desc = r.desc + reqs.get_text()

            companies = tempObj.find(settings['hh.ru']['companies'][0], settings['hh.ru']['companies'][1])
            r.company = companies.get_text()

            dates = tempObj.find(settings['hh.ru']['dates'][0], settings['hh.ru']['dates'][1])
            r.date = dates.get_text()

            r.setmd5()

            # log(r)
            if r not in oldresults:
                results.append(r)

        ipage+=1
        html = urlopen(settings['hh.ru']['url'] + "&page={0}".format(ipage))
        bsObj = BeautifulSoup(html.read(),"html.parser")
        vacancies = bsObj.findAll(settings['hh.ru']['outer_block'][0],settings['hh.ru']['outer_block'][1]) # outer block


    serialize(results,dumpfile)


    oldresults.extend(results)

    if len(oldresults) > 0:
        # displayresults
        root = Tk()
        root.title("Job Parser Results")
        root.geometry('900x400')

        tree = ttk.Treeview(root,height="20")
        tree.bind("<Button-3>", rightclick)
        tree["columns"]=("label","salary","descriprion","date","company","url")
        tree.column("#0", width=7)
        tree.column("#1", width=120)
        tree.column("#2", width=110)
        tree.column("#3", width=250)
        tree.column("#4", width=120)
        tree.column("#5", width=110)
        tree.column("#6", width=0)
        tree.heading("#0",text="№", command="")
        tree.heading("label",text="Заголовок")
        tree.heading("salary",text="з/п")
        tree.heading("descriprion",text="Описание")
        tree.heading("date",text="Дата публикации")
        tree.heading("company",text="Компания")
        tree.heading("url",text="Ссылка")
        tree.pack(expand=True, fill='both')

        for i,item in enumerate(oldresults):
            tree.insert("","end",text=str(i+1), values=(item.label,item.salary,item.desc,item.date,item.company,item.url))
        root.mainloop()