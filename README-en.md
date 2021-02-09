# pyfund
This is a python script that it has capability to analyze Chinese funds.

### **Introduction**
This script can crawl Chinese funds information and draw a trend chart of fund. The filter middleware is wrote in fundfilter.py, it can filter and choose funds based on the simple principle of mathematical expectation. For the further improvement, BP artificial neural network(ANN), Extreme learning machine, or Fuzzy control would be a option to be added into the filter middleware.



### **Flowchart**
```flow
st=>start
op0=>operation: Crawl funds list
op1=>operation: Analyze fund
op2=>operation: Choose your favorite
e=>end

st->op0->op1->op2->e
```

### **Legal statement**
* This script was wrote by my own interest, which is not completely perfect. The filter method was very simple and crude. The funds would be selected in condition of that it rose in a cycle like 90 days and tanked for 60% in recent 10 days, which has not been not mathematically proven yet. There is no guarantee that the selected funds would rise, since the stock holding ratio and policy is excluded from this script.
* This script can only be used for communication and learning purposes, not for commercial purposes。
* Anyone who uses this script to invest a fund, whether it's price rises or tanks, has nothing to do with me.


### **Why do I wrote this script？**
Your boss might not pay the enough salary for you, so we have to earn some spare money after work. Anyway, I can also play python by the way.

### **OS Platform**
Windows/Linux/macOS are supported

### **Necessary Envorinment**
* python3
* matplotlib
* PyExecJS

You can excute the following up command line in a python-installed platform:
```
pip3 install matplotlib
pip3 install PyExecJ
```

### **How to excute it?**
* To crewl funds information
```
python3 pyfund.py -s
```

* To show trend chart of fund
```
python3 pyfund.py -a
```

* To crewl funds information and then show trend chart of fund
```
python3 pyfund.py -s -a
```

